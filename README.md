# DQX offline bundle

Everything needed to install [Databricks Labs DQX](https://github.com/databrickslabs/dqx) 0.16.0 on a Databricks cluster **without internet access**, plus a short test notebook.

## Contents

- `dqx_wheels/`: 27 unmodified wheels from PyPI (`databricks-labs-dqx==0.16.0` and its dependencies) for **Linux x86_64, CPython 3.11 and 3.12**. The 5 compiled dependencies (cffi, charset_normalizer, pydantic_core, pyyaml, sqlalchemy) are included for both Python versions; the 17 pure-Python wheels are shared. Tested on **DBR 15.4 LTS** (Python 3.11, standard and dedicated access mode) and **DBR 16.4 LTS** (Python 3.12). Two pins on top of stock: `databricks-sdk>=0.120,<1` and `protobuf<5`.
- `DQX_offline_install_and_test.py` / `.ipynb`: the same notebook in two formats. Installs DQX offline, profiles `samples.bakehouse.sales_transactions`, runs built-in checks plus one custom check, and prints the results. It writes nothing.
- `SHA256SUMS.txt`: checksums for every wheel.

## Use

1. Upload the `dqx_wheels/` folder to a UC volume or a workspace folder.
2. Import the notebook, set `WHEELS_DIR` to that folder (the only variable), and run all cells on a classic cluster (DBR 15.4 LTS or 16.4 LTS, x86_64).

The install is `%pip install --no-index --find-links $WHEELS_DIR databricks-labs-dqx==0.16.0`, so nothing is fetched from the internet.

## Rebuild the wheels yourself

```
for PY in 3.11 3.12; do
  pip download databricks-labs-dqx==0.16.0 "databricks-sdk>=0.120,<1" "protobuf<5" \
    --only-binary=:all: --platform manylinux2014_x86_64 --platform manylinux_2_28_x86_64 \
    --python-version $PY --implementation cp -d dqx_wheels
done
```

A fresh download may pick slightly newer dependency versions than the tested set here.

## What the install changes on the cluster

It is a notebook-scoped `%pip install`, so it affects only that notebook's Python environment. On DBR 15.4 LTS it adds DQX, blueprint, sqlalchemy, pydantic_core, annotated-types and typing-inspection. It also upgrades databricks-sdk (0.20.0 to 0.154.0), **pydantic (1.10.6 to 2.14.1)**, protobuf (4.24.1 to 4.25.9), PyYAML (6.0 to 6.0.3) and typing_extensions. On DBR 16.4 LTS it adds DQX, blueprint and sqlalchemy, and upgrades databricks-sdk, protobuf and PyYAML. `pip check` is clean on 16.4. On 15.4 it reports only `pygobject requires pycairo`, which the install does not touch.

## Licences

The wheels are third-party packages redistributed unmodified, and each keeps its own licence inside the wheel's metadata. `databricks-labs-dqx` and `databricks-labs-blueprint` are under the Databricks License, which allows use only in connection with the Databricks Services. Copies of that licence and the NOTICE files are in `LICENSES/`. The other dependencies are under open-source licences (Apache-2.0, MIT, BSD and similar). This repository adds only the notebook, README and checksums. It is not an official Databricks product.
