# DQX offline bundle

Everything needed to install [Databricks Labs DQX](https://github.com/databrickslabs/dqx) 0.16.0 on a Databricks cluster **without internet access**, plus a short test notebook.

## Contents

- `dqx_wheels/`: 22 unmodified wheels from PyPI (`databricks-labs-dqx==0.16.0` and its dependencies) for **Linux x86_64, CPython 3.12**, which matches DBR 16.4 / 17.3 / 18 LTS. Two pins on top of stock: `databricks-sdk>=0.120,<1` and `protobuf<5`.
- `DQX_offline_install_and_test.py` / `.ipynb`: the same notebook in two formats. Installs DQX offline, profiles `samples.bakehouse.sales_transactions`, runs built-in checks plus one custom check, and prints the results. It writes nothing.
- `SHA256SUMS.txt`: checksums for every wheel.

## Use

1. Upload the `dqx_wheels/` folder to a UC volume or a workspace folder.
2. Import the notebook, set `WHEELS_DIR` to that folder (the only variable), and run all cells on a classic cluster (DBR 16.4 LTS or later, x86_64).

The install is `%pip install --no-index --find-links $WHEELS_DIR databricks-labs-dqx==0.16.0`, so nothing is fetched from the internet.

## Rebuild the wheels yourself

```
pip download databricks-labs-dqx==0.16.0 "databricks-sdk>=0.120,<1" "protobuf<5" \
  --only-binary=:all: --platform manylinux2014_x86_64 --platform manylinux_2_28_x86_64 \
  --python-version 3.12 --implementation cp -d dqx_wheels
```

A fresh download may pick slightly newer dependency versions than the tested set here.

## Licences

The wheels are third-party packages redistributed unmodified, and each keeps its own licence inside the wheel's metadata. `databricks-labs-dqx` and `databricks-labs-blueprint` are under the Databricks License, which allows use only in connection with the Databricks Services. Copies of that licence and the NOTICE files are in `LICENSES/`. The other dependencies are under open-source licences (Apache-2.0, MIT, BSD and similar). This repository adds only the notebook, README and checksums. It is not an official Databricks product.
