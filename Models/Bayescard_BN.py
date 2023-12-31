from Pgmpy.models import BayesianModel
import numpy as np
import copy
import logging
import time
from Models.BN_single_model import BN_Single
import itertools

logger = logging.getLogger(__name__)


def build_meta_info(column_names, null_values):
    meta_info = dict()
    fanout_attr = []
    fanout_attr_inverse = []
    fanout_attr_positive = []
    meta_info['null_values'] = dict()
    for i, col in enumerate(column_names):
        if col is not None and 'mul_' in col:
            fanout_attr.append(col)
            if '_nn' in col:
                fanout_attr_inverse.append(col)
            else:
                fanout_attr_positive.append(col)
        meta_info['null_values'][col] = null_values[i]
    meta_info['fanout_attr'] = fanout_attr
    meta_info['fanout_attr_inverse'] = fanout_attr_inverse
    meta_info['fanout_attr_positive'] = fanout_attr_positive
    meta_info['n_distinct_mapping'] = dict()
    #For continuous variables, pandas uses a default equal-width interval, so some values are undercounted/overcounted
    #Thus the following two lines are hard coded for JOB to account for this effect.
    #This should be very easy to make it automatic in the future.
    meta_info['n_distinct_mapping']['movie_keyword.keyword_id']={117: 8, 8200: 10, 398: 5, 7084: 20}
    meta_info['n_distinct_mapping']['movie_companies.company_id']={22956: 30}
    return meta_info


class Bayescard_BN(BN_Single):
    """
    Build a single Bayesian Network for a single table using pgmpy
    """

    def __init__(self, table_name, meta_info=None, nrows=None, method='Pome', debug=True, infer_algo=None):
        """
        infer_algo: inference method, choose between 'exact', 'BP'
        """
        BN_Single.__init__(self, table_name, meta_info, method, debug)
        self.nrows = nrows
        self.infer_algo = infer_algo
        self.infer_machine = None
        self.cpds = None

    def realign(self, encode_value, n_distinct):
        """
        Discard the invalid and duplicated values in encode_value and n_distinct and realign the two
        """
        if type(encode_value) != list and type(n_distinct) != list:
            return encode_value, n_distinct

        assert len(encode_value) == len(n_distinct)
        res_value = []
        res_n_distinct = []
        for i, c in enumerate(encode_value):
            if c is not None:
                if c in res_value:
                    index = res_value.index(c)
                    res_n_distinct[index] += n_distinct[i]
                    res_n_distinct[index] = min(res_n_distinct[index], 1)
                else:
                    res_value.append(c)
                    res_n_distinct.append(n_distinct[i])
        return res_value, res_n_distinct

    def build_from_data(self, dataset, attr_type=None, sample_size=1000000, n_mcv=30, n_bins=60, ignore_cols=['id'],
                        algorithm="chow-liu", drop_na=True, max_parents=-1, root=0, n_jobs=8, discretized=False):
        """ Build the Pomegranate model from data, including structure learning and paramter learning
            ::Param:: dataset: pandas.dataframe
                      attr_type: type of attributes (binary, discrete or continuous)
                      sample_size: subsample the number of rows to use to learn structure
                      n_mcv: for categorical data we keep the top n most common values and bin the rest
                      n_bins: number of bins for histogram, larger n_bins will provide more accuracy but less efficiency
            for other parameters, pomegranate gives a detailed explaination:
            https://pomegranate.readthedocs.io/en/latest/BayesianNetwork.html
        """
        self.algorithm = algorithm
        if algorithm != "junction":
            discrete_table = self.learn_model_structure(dataset, self.nrows, attr_type, sample_size,
                                                        n_mcv, n_bins, ignore_cols, algorithm,
                                                        drop_na, max_parents, root, n_jobs,
                                                        return_dataset=True, discretized=discretized)
        else:
            discrete_table = self.learn_model_structure(dataset, self.nrows, attr_type, sample_size,
                                                        n_mcv, n_bins, ignore_cols, 'chow-liu',
                                                        drop_na, max_parents, root, n_jobs,
                                                        return_dataset=True, discretized=discretized)
        spec = []
        orphans = []
        for i, parents in enumerate(self.structure):
            for p in parents:
                spec.append((self.node_names[p], self.node_names[i]))
            if not parents:
                orphans.append(self.node_names[i])
        if self.debug:
            logger.info(f"Model spec{spec}")
        self.model = BayesianModel(spec)
        for o in orphans:
            self.model.add_node(o)
        logger.info('calling pgm.BayesianModel.fit...')
        t = time.time()
        self.model.fit(discrete_table)
        if algorithm == "junction":
            try:
                self.model = self.model.to_junction_tree()
            except:
                self.model = self.model
                logger.warning(
                    "This BN is not able to transform into junction tree, probably because it's not connected, just use BN")
        logger.info(f"done, took {time.time() - t} secs.")
        print(f"done, parameter learning took {time.time() - t} secs.")
        #self.init_inference_method()

    def init_inference_method(self, algorithm=None):
        """
        Initial the inference method for query
        """
        if algorithm:
            self.infer_algo = algorithm
        if self.infer_algo is None:
            if self.algorithm == "chow-liu":
                self.infer_algo = "exact"
            else:
                self.infer_algo = "BP"

        if self.infer_algo == "exact-jit":
            assert self.algorithm == "chow-liu", "Currently JIT only supports CLT"
            from Pgmpy.inference import VariableEliminationJIT
            cpds, topological_order, topological_order_node = self.align_cpds_in_topological()
            self.cpds = cpds
            self.topological_order = topological_order
            self.topological_order_node = topological_order_node
            self.infer_machine = VariableEliminationJIT(self.model, cpds, topological_order, topological_order_node,
                                                       self.fanouts)
        elif self.infer_algo == "exact-jit-torch":
            assert self.algorithm == "chow-liu", "Currently JIT only supports CLT"
            from Pgmpy.inference import VariableEliminationJIT_torch
            cpds, topological_order, topological_order_node = self.align_cpds_in_topological()
            self.cpds = cpds
            self.topological_order = topological_order
            self.topological_order_node = topological_order_node
            self.infer_machine = VariableEliminationJIT_torch(self.model, cpds, topological_order, topological_order_node,
                                                             self.fanouts)
        elif self.infer_algo == "exact":
            from Pgmpy.inference import VariableElimination
            self.infer_machine = VariableElimination(self.model)
        elif self.infer_algo == "BP":
            try:
                # Belief Propogation won't work if the model graph is not connected
                from Pgmpy.inference import BeliefPropagation
                self.infer_machine = BeliefPropagation(self.model)
                self.infer_machine.calibrate()
            except:
                logger.warning("Graph is not connected, we have automatically set the "
                               "inference algorithm to exact. If you would like to use BP,"
                               "please manually connect the graph.")
                from Pgmpy.inference import VariableElimination
                self.infer_algo = "exact"
                self.infer_machine = VariableElimination(self.model)
        elif self.infer_algo == "sampling":
            from Pgmpy.sampling import BayesianModelSampling
            self.infer_machine = BayesianModelSampling(self.model)
            logger.warning("Using sampling as an inference algorithm is very inefficient")
        elif self.infer_algo == "progressive_sampling":
            cpds, topological_order, topological_order_node = self.align_cpds_in_topological()
            self.cpds = cpds
            self.topological_order = topological_order
            self.topological_order_node = topological_order_node
        else:
            raise NotImplemented

    def continuous_range_map(self, col, range):
        def cal_coverage(l, r, target):
            tl = target.left
            tr = target.right
            if l >= tr: return 0
            if r <= tl: return 0
            if r > tr:
                if l < tl:
                    return 1
                else:
                    return (tr - l) / (tr - tl)
            else:
                if l > tl:
                    return (r - l) / (tr - tl)
                else:
                    return (r - tl) / (tr - tl)

        def binary_search(i, j):
            # binary_search to find a good starting point
            if i == j:
                return i
            m = int(i + (j - i) / 2)
            interval = self.mapping[col][m]
            if left >= interval.right:
                return binary_search(m, j)
            elif right <= interval.left:
                return binary_search(i, m)
            else:
                return m

        (left, right) = range
        if left is None: left = -np.Inf
        if right is None: right = np.Inf
        query = []
        coverage = []
        start_point = binary_search(0, len(self.mapping[col]))
        start_point_left = start_point
        start_point_right = start_point + 1
        indicator_left = True
        indicator_right = True
        while (start_point_left >= 0 and start_point_right < len(self.mapping[col])
               and (indicator_left or indicator_right)):
            if indicator_left:
                cover = cal_coverage(left, right, self.mapping[col][start_point_left])
                if cover != 0:
                    query.append(start_point_left)
                    coverage.append(cover)
                    start_point_left -= 1
                else:
                    indicator_left = False

            if indicator_right:
                cover = cal_coverage(left, right, self.mapping[col][start_point_right])
                if cover != 0:
                    query.append(start_point_right)
                    coverage.append(cover)
                    start_point_right += 1
                else:
                    indicator_right = False
        return query, np.asarray(coverage)

    def one_iter_of_infer(self, query, n_distinct):
        """Performance a BP in random order.
           This adapts the BP implemented in pgympy package itself.
        """
        copy_query = copy.deepcopy(query)
        sampling_order = copy.deepcopy(self.node_names)
        np.random.shuffle(sampling_order)

        p_estimate = 1
        for attr in sampling_order:
            if attr in query:
                val = copy_query.pop(attr)
                probs = self.infer_machine.query([attr], evidence=copy_query).values
                if any(np.isnan(probs)):
                    p_estimate = 0
                    break
                p = probs[val] / (np.sum(probs)) * n_distinct[attr]
                p_estimate *= p

        return p_estimate

    def query_sampling(self, query, sample_size=10000):
        gen = self.infer_machine.forward_sample(size=sample_size)
        query_str = ""
        n = 0
        for attr in query:
            query_str += attr
            if type(query[attr]) != list:
                query_str += (attr + " == " + str(query[attr]))
            elif len(query[attr]) == 1:
                query_str += (attr + " == " + str(query[attr][0]))
            else:
                query_str += (attr + " in " + str(query[attr]))
            if n != len(query) - 1:
                query_str += " and "
        card = len(gen.query(query_str))
        return card / sample_size

    def query_decoding(self, query, coverage=None, epsilon=0.5):
        """
        Convert the query to the encodings BN recognize
        """
        n_distinct = dict()
        for attr in query:
            if self.attr_type[attr] == 'continuous':
                if coverage is None:
                    n_d_temp = None
                    if type(query[attr]) == tuple:
                        l = max(self.domain[attr][0], query[attr][0])
                        r = min(self.domain[attr][1], query[attr][1])
                    else:
                        l = query[attr]-epsilon
                        r = query[attr]+epsilon
                        if attr in self.n_distinct_mapping:
                            if query[attr] in self.n_distinct_mapping[attr]:
                                n_d_temp = self.n_distinct_mapping[attr][query[attr]]
                    if l > r:
                        return None, None
                    query[attr], n_distinct[attr] = self.continuous_range_map(attr, (l, r))
                    if n_d_temp is not None:
                        n_distinct[attr] *= n_d_temp
                else:
                    n_distinct[attr] = coverage[attr]
            elif type(query[attr]) == tuple:
                query_list = []
                if self.null_values is None or len(self.null_values) == 0 or attr not in self.null_values:
                    for val in self.encoding[attr]:
                        if query[attr][0] <= val <= query[attr][1]:
                            query_list.append(val)
                else:
                    for val in self.encoding[attr]:
                        if val != self.null_values[attr] and query[attr][0] <= val <= query[attr][1]:
                            query_list.append(val)
                encode_value = self.apply_encoding_to_value(query_list, attr)
                if encode_value is None or (encode_value == []):
                    return None, None
                n_distinct[attr] = self.apply_ndistinct_to_value(encode_value, query_list, attr)
                query[attr], n_distinct[attr] = self.realign(encode_value, n_distinct[attr])
            else:
                encode_value = self.apply_encoding_to_value(query[attr], attr)
                if encode_value is None or (encode_value == []):
                    return None, None
                n_distinct[attr] = self.apply_ndistinct_to_value(encode_value, query[attr], attr)
                query[attr], n_distinct[attr] = self.realign(encode_value, n_distinct[attr])
        return query, n_distinct

    def get_fanout_values(self, fanout_attrs):
        if len(fanout_attrs) == 1:
            return self.fanouts[fanout_attrs[0]]
        else:
            fanout_attrs_shape = tuple([len(self.fanouts[i]) for i in fanout_attrs])
            res = None
            for i in fanout_attrs:
                if res is None:
                    res = self.fanouts[i]
                else:
                    res = np.outer(res, self.fanouts[i]).reshape(-1)
            return res.reshape(fanout_attrs_shape)

    def align_cpds_in_topological(self):
        cpds = self.model.cpds
        sampling_order = []
        while len(sampling_order) < len(self.structure):
            for i, deps in enumerate(self.structure):
                if i in sampling_order:
                    continue  # already ordered
                if all(d in sampling_order for d in deps):
                    sampling_order.append(i)
        topological_order = sampling_order
        topological_order_node = [self.node_names[i] for i in sampling_order]
        new_cpds = []
        for n in topological_order_node:
            for cpd in cpds:
                if cpd.variable == n:
                    new_cpds.append(cpd)
                    break
        assert len(cpds) == len(new_cpds)
        return new_cpds, topological_order, topological_order_node


    def get_condition(self, evidence, cpd, topological_order_node, var_evidence, n_distinct=None, hard_sample=False):
        values = cpd.values
        if evidence[0][0] == -1:
            assert len(values.shape) == 1
            if n_distinct:
                probs = values[var_evidence] * n_distinct
            else:
                probs = values[var_evidence]
            return_prob = np.sum(probs)
            probs = probs / return_prob  # re-normalize
            new_evidence = np.random.choice(var_evidence, p=probs, size=evidence.shape[-1])
        else:
            scope = cpd.variable
            condition = cpd.variables[1:]
            condition_ind = [topological_order_node.index(c) for c in condition]
            condition_evidence = evidence[condition_ind]
            # the following is hardcoded for fast computation
            if len(condition) == 1:
                probs = values[:, condition_evidence[0]]
            elif len(condition) == 2:
                probs = values[:, condition_evidence[0], condition_evidence[1]]
            elif len(condition) == 3:
                probs = values[:, condition_evidence[0], condition_evidence[1], condition_evidence[2]]
            elif len(condition) == 4:
                probs = values[:, condition_evidence[0], condition_evidence[1], condition_evidence[2],
                        condition_evidence[3]]
            elif len(condition) == 5:
                probs = values[:, condition_evidence[0], condition_evidence[1], condition_evidence[2],
                        condition_evidence[3], condition_evidence[4]]
            elif len(condition) == 6:
                probs = values[:, condition_evidence[0], condition_evidence[1], condition_evidence[2],
                        condition_evidence[3], condition_evidence[4], condition_evidence[5]]
            elif len(condition) == 7:
                probs = values[:, condition_evidence[0], condition_evidence[1], condition_evidence[2],
                        condition_evidence[3], condition_evidence[4], condition_evidence[5],
                        condition_evidence[6]]
            else:
                # no more efficient tricks
                probs = np.zeros((values.shape[0], evidence.shape[-1]))
                for j in range(values.shape[0]):
                    probs[j, :] = values[j]
            #print(len(var_evidence))
            #print(probs.shape)
            if n_distinct:
                probs = (probs[var_evidence, :].transpose() * n_distinct).transpose()
            else:
                probs = probs[var_evidence, :]
            #print(probs.shape)
            return_prob = np.sum(probs, axis=0)
            #print(return_prob.shape)
            probs = (probs / return_prob)
            probs[np.isnan(probs)] = 0
            if hard_sample:
                probs += 1e-7
                probs = probs/np.sum(probs, axis=0)
                new_evidence = np.asarray([np.random.choice(var_evidence, p=probs[:,i]) for i in range(evidence.shape[-1])])
                #print(probs.shape)
            else:
                generate_probs = probs.mean(axis=1)
                if np.sum(generate_probs) == 0:
                    return 0, None
                generate_probs = generate_probs / np.sum(generate_probs)
                new_evidence = np.random.choice(var_evidence, p=generate_probs, size=evidence.shape[-1])
        return return_prob, new_evidence



    def progressive_sampling(self, query, sample_size, n_distinct=None, hard_sample=False):
        """Using progressive sampling method as described in Naru paper"""
        if self.cpds is None:
            cpds, topological_order, topological_order_node = self.align_cpds_in_topological()
            self.cpds = cpds
            self.topological_order_node = topological_order_node

        evidence = np.zeros((len(self.topological_order_node), sample_size), dtype=int) - 1
        probs = np.ones(sample_size)
        for i, node in enumerate(self.topological_order_node):
            if node in query:
                var_evidence = query[node]
                if n_distinct:
                    n_distinct_value = n_distinct[node]
                else:
                    n_distinct_value = None
            else:
                var_evidence = np.arange(self.cpds[i].values.shape[0])
                n_distinct_value = None
            if type(var_evidence) == int:
                var_evidence = [var_evidence]
            new_probs, new_evidence = self.get_condition(evidence, self.cpds[i],
                                                         self.topological_order_node, var_evidence, 
                                                         n_distinct_value, hard_sample=hard_sample)
            if new_evidence is None:
                return 0
            evidence[i, :] = new_evidence
            probs *= new_probs
        return np.sum(probs) / evidence.shape[-1]

    def progressive_sampling_expectation(self, query, fanout_attrs, sample_size, n_distinct=None, hard_sample=False):
        """Using progressive sampling to do expectation"""
        if self.cpds is None:
            cpds, topological_order, topological_order_node = self.align_cpds_in_topological()
            self.cpds = cpds
            self.topological_order_node = topological_order_node

        evidence = np.zeros((len(self.topological_order_node), sample_size), dtype=int) - 1
        exps = np.ones(sample_size)
        for i, node in enumerate(self.topological_order_node):
            is_fanout = False
            if node in query:
                var_evidence = query[node]
                if n_distinct:
                    n_distinct_value = n_distinct[node]
                else:
                    n_distinct_value = None
            else:
                var_evidence = np.arange(self.cpds[i].values.shape[0])
                n_distinct_value = None
                if node in fanout_attrs:
                    # fanout attr for expectation computing
                    is_fanout = True
            #print(is_fanout)
            if type(var_evidence) == int:
                var_evidence = [var_evidence]
            new_probs, new_evidence = self.get_condition(evidence, self.cpds[i],
                                                         self.topological_order_node, var_evidence, 
                                                         n_distinct_value, hard_sample=hard_sample)
            if new_evidence is None:
                return 0
            evidence[i, :] = new_evidence
            exps *= new_probs
            if is_fanout:
                exps *= self.fanouts[node][new_evidence]
        return np.sum(exps) / evidence.shape[-1]


    def query(self, query, num_samples=1, n_distinct=None, coverage=None, return_prob=False, sample_size=1000, hard_sample=False):
        """Probability inference using Loopy belief propagation. For example estimate P(X=x, Y=y, Z=z)
           ::Param:: query: dictionary of the form {X:x, Y:y, Z:z}
                     x,y,z can only be a single value
                     num_samples: how many times to run inference, only useful for approaximate algo
                     an approaximation, we might to run it for multiple times and take the average.
                     coverage: the same as ndistinct for continous data
                     return_prob: if true, return P(X=x, Y=y, Z=z)
                                  else return P(X=x, Y=y, Z=z)*nrows
        """
        assert self.infer_algo is not None, "must call .init_inference_method() first"
        if self.infer_algo == "sampling":
            p_estimate = self.query_sampling(query, sample_size)
            if return_prob:
                return (p_estimate, self.nrows)
            return p_estimate * self.nrows

        nrows = self.nrows
        if n_distinct is None:
            query, n_distinct = self.query_decoding(query, coverage)
        #print(f"decoded query is {query}")
        if query is None:
            if return_prob:
                return 0, nrows
            else:
                return 0

        if self.infer_algo == "progressive_sampling":
            p_estimate = self.progressive_sampling(query, sample_size, n_distinct, hard_sample=hard_sample)
            if return_prob:
                return (p_estimate, self.nrows)
            return p_estimate * self.nrows

        elif self.infer_algo == "exact-jit" or self.infer_algo == "exact-jit-torch":
            p_estimate = self.infer_machine.query(query, n_distinct)
            if return_prob:
                return (p_estimate, self.nrows)
            return p_estimate * self.nrows

        elif self.infer_algo == "exact" or num_samples == 1:
            sampling_order = list(query.keys())
            p_estimate = 1
            for attr in sampling_order:
                if attr in query:
                    val = query.pop(attr)
                    probs = self.infer_machine.query([attr], evidence=query).values
                    if np.any(np.isnan(probs)):
                        p_estimate = 0
                        break
                    p = np.sum(probs[val] * n_distinct[attr])
                    p_estimate *= p

        else:
            p_estimates = []
            for i in range(num_samples):
                p_estimates.append(self.one_iter_of_infer(query, n_distinct))
            p_estimate = sum(p_estimates) / num_samples

        if return_prob:
            return (p_estimate, nrows)
        return round(p_estimate * nrows)


    def expectation(self, query, fanout_attrs, num_samples=1, n_distinct=None, coverage=None,
                    return_prob=False, sample_size=1000, hard_sample=False):
        """
        Calculating the expected value E[P(Q|F)*F]
        Parameters
        ----------
        fanout_attrs: a list of fanout variables F, where we would like to compute the expectation
        Rest parameters: the same as previous function .query().
        """
        if fanout_attrs is None or len(fanout_attrs) == 0:
            return self.query(query, num_samples, n_distinct, coverage, return_prob, sample_size)

        elif self.infer_algo == "progressive_sampling":
            if n_distinct is None:
                query, n_distinct = self.query_decoding(query, coverage)
            exp = self.progressive_sampling_expectation(query, fanout_attrs, sample_size, n_distinct, hard_sample)
            if return_prob:
                return exp, self.nrows
            else:
                return exp * self.nrows

        elif self.infer_algo == "exact-jit" or self.infer_algo == "exact-jit-torch":
            if n_distinct is None:
                query, n_distinct = self.query_decoding(query, coverage)
            exp = self.infer_machine.expectation(query, fanout_attrs, n_distinct)
            if return_prob:
                return exp, self.nrows
            else:
                return exp * self.nrows

        else:
            query_prob = copy.deepcopy(query)
            probsQ, _ = self.query(query_prob, num_samples, n_distinct, coverage, True)
            if probsQ == 0:
                if return_prob:
                    return 0, self.nrows
                else:
                    return 0
            if n_distinct is None:
                query, n_distinct = self.query_decoding(query, coverage)
            if query is None:
                if return_prob:
                    return 0, self.nrows
                else:
                    return 0
            
            probsQF = self.infer_machine.query(fanout_attrs, evidence=query).values
            
            if np.any(np.isnan(probsQF)):
                if return_prob:
                    return 0, self.nrows
                else:
                    return 0
            else:
                probsQF = probsQF / (np.sum(probsQF))
                
            fanout_attrs_shape = tuple([len(self.fanouts[i]) for i in fanout_attrs])
            probsQF = probsQF.reshape(fanout_attrs_shape)
            exp = np.sum(probsQF * self.get_fanout_values(fanout_attrs)) * probsQ
            if return_prob:
                return exp, self.nrows
            else:
                return exp * self.nrows

