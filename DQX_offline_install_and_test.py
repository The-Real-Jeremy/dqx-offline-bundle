# Databricks notebook source
# MAGIC %md
# MAGIC # DQX offline install + test
# MAGIC
# MAGIC Shows that the **DQX library (databricks-labs-dqx 0.16.0)** installs with **no internet** and runs: it profiles a
# MAGIC `samples.bakehouse` table and applies data-quality checks, including one custom check defined in this notebook.
# MAGIC **It only prints. Nothing is written anywhere.**
# MAGIC
# MAGIC **Before you start:** copy the unzipped `dqx_wheels` folder (22 `.whl` files) into a UC Volume
# MAGIC (Catalog Explorer → volume → *Upload to this volume*) or a workspace folder (Workspace → *Import*).
# MAGIC Set its path in the first cell. Use a classic cluster on DBR 16.4 / 17.3 / 18 LTS (x86_64).

# COMMAND ----------

WHEELS_DIR = "/Volumes/<catalog>/<schema>/<volume>/dqx_wheels"   # or "/Workspace/Users/<you>/dqx_wheels"

# COMMAND ----------

# MAGIC %pip install --no-index --find-links $WHEELS_DIR databricks-labs-dqx==0.16.0

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

from databricks.labs.dqx.__about__ import __version__
print("DQX version:", __version__)

# COMMAND ----------

df = spark.table("samples.bakehouse.sales_transactions")
print(df.count(), "rows")
display(df.limit(5))

# COMMAND ----------

# Profile the whole table, then let DQX suggest rules from the profile.
from databricks.sdk import WorkspaceClient
from databricks.labs.dqx.profiler.profiler import DQProfiler
from databricks.labs.dqx.profiler.generator import DQGenerator

ws = WorkspaceClient()
summary, profiles = DQProfiler(ws).profile(df, options={"sample_fraction": None, "limit": None})

print("Summary statistics:")
for column, stats in summary.items():
    print(f"  {column}: {stats}")

print("\nGenerated rules:")
for rule in DQGenerator(ws).generate_dq_rules(profiles):
    print(f"  {rule['check']['function']}({rule['check']['arguments']})")

# COMMAND ----------

# A custom check: flag sales outside trading hours. A check returns a condition that is TRUE for a failing row.
import pyspark.sql.functions as F
from databricks.labs.dqx.check_funcs import make_condition
from databricks.labs.dqx.rule import register_rule

@register_rule("row")
def is_within_trading_hours(column: str, open_hour: int, close_hour: int):
    hour = F.hour(F.col(column))
    return make_condition(
        (hour < open_hour) | (hour >= close_hour),
        F.concat(F.lit(f"{column} outside trading hours: "), F.col(column).cast("string")),
        f"{column}_outside_trading_hours",
    )

# COMMAND ----------

# Checks as YAML: built-in functions plus the custom one.
# Note: in is_in_list, string values need inner quotes ("'visa'"); a bare word is read as a column name.
import yaml

checks = yaml.safe_load("""
- criticality: error
  check: {function: is_not_null, arguments: {column: transactionID}}
- criticality: error
  check: {function: is_unique, arguments: {columns: [transactionID]}}
- criticality: error
  check: {function: is_in_list, arguments: {column: paymentMethod, allowed: ["'visa'", "'mastercard'", "'amex'"]}}
- name: bulk_order
  criticality: error
  check: {function: is_in_range, arguments: {column: quantity, min_limit: 1, max_limit: 20}}
- criticality: warn
  check: {function: is_within_trading_hours, arguments: {column: dateTime, open_hour: 6, close_hour: 21}}
""")

# COMMAND ----------

from databricks.labs.dqx.engine import DQEngine

dq = DQEngine(ws)
custom = {"is_within_trading_hours": is_within_trading_hours}
status = dq.validate_checks(checks, custom_check_functions=custom)
print("Checks valid:", not status.has_errors, status.to_string())

valid, invalid = dq.apply_checks_by_metadata_and_split(df, checks, custom_check_functions=custom)
print("Valid rows (no errors):          ", valid.count())
print("Invalid rows (errors or warnings):", invalid.count())

# COMMAND ----------

# Failures per check, and a few failing rows with DQX's reasons.
results = dq.apply_checks_by_metadata(df, checks, custom_check_functions=custom)
issues = results.select(F.explode(F.concat(F.coalesce("_errors", F.array()), F.coalesce("_warnings", F.array()))).alias("issue"))
display(issues.groupBy("issue.name").count())
display(invalid.select("transactionID", "dateTime", "quantity", "paymentMethod", "_errors", "_warnings").limit(10))
