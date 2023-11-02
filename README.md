### BayesCard demo, just for testing

1. Environment Setup (Please note that the absolute paths in the .yml file need to be modified.). If `environment.yml`` fails to install, you can manually install the dependencies as follows.:

```
conda create -n bayes python=3.7.7
conda activate bayes

pip install arff==0.9 asn1crypto==0.24.0 atomicwrites==1.3.0 attrs==19.1.0 bloom-filter==1.3 certifi==2019.3.9 cffi==1.12.3 chardet==3.0.4 cloudpickle==1.2.1 colorama==0.4.1 cryptography==2.9.2 dask==1.2.0 decorator==4.4.0 ete3==3.1.1 idna==2.6 joblib==0.13.2 keyring==10.6.0 keyrings-alt==3.0 kiwisolver==1.1.0 lark-parser==0.7.1 locket==0.2.0 mock==3.0.4 more-itertools==7.0.0 mpmath==1.1.0 networkx==2.3 numexpr==2.6.9 numpy==1.16.3 pandas==0.23.4 partd==1.0.0 patsy==0.5.1 pgmpy==0.1.13 pluggy==0.9.0 py==1.8.0 py4j==0.10.8.1 pybind11==2.3.0 pycparser==2.19 pycrypto==2.6.1 pydot==1.4.1 pyparsing==2.4.0 pyqt5==5.12.1 matplotlib==3.0.3 pyqt5-sip==4.19.15 pytest==4.4.1 python-dateutil==2.7.5 pytz==2018.7 pyverdict==0.1.3.2 pyxdg==0.25 pyyaml==3.12 requests==2.18.4 scikit-learn==0.20.3 scipy==1.2.1 secretstorage==2.3.1 six==1.12.0 sklearn==0.0 spflow==0.0.34 sqlalchemy==1.3.11 sqlparse==0.3.0 statsmodels==0.9.0 sympy==1.4 tables==3.5.1 torch==1.7.1 toolz==0.9.0 tqdm==4.31.1 typing-extensions==3.7.4.3 urllib3==1.22 var-dump==1.2 wincertstore==0.2

```

2. Since the pre-trained dictionary has already been uploaded, you only need to start the server by running `python bayes_inference.py`
3. Test by running `python client.py`


### Tips for training

During training, we do not consider columns with a large number of distinct values (NDV) or non-trivial types. This is consistent with the statistical information completion required for virtual index recommendations, as these excluded columns also do not take these factors into account.