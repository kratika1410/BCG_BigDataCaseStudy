# -*- coding: utf-8 -*-
"""analytics

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VHy-BqxqczwAhBevGNfdnAxYqU7DE7zt
"""

# analytics

# importing required packages
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, when, count, countDistinct
from pyspark.sql.window import Window
from pyspark.sql import functions as F


#Analysis 1
def analyze_crashes_with_male_fatalities(spark, charges_df, primary_person_df, output_path):
    # Rename columns to avoid conflicts during the join
    # Aliases for the columns in charges_df
    charges_df = charges_df.withColumnRenamed("PRSN_NBR", "charges_prsn_nbr")
    charges_df = charges_df.withColumnRenamed("CRASH_ID", "charges_crash_id")
    charges_df = charges_df.withColumnRenamed("UNIT_NBR", "charges_unit_nbr")

    # Aliases for the columns in primary_person_df
    primary_person_df = primary_person_df.withColumnRenamed("PRSN_NBR", "primary_prsn_nbr")
    primary_person_df = primary_person_df.withColumnRenamed("CRASH_ID", "primary_crash_id")
    primary_person_df = primary_person_df.withColumnRenamed("UNIT_NBR", "primary_unit_nbr")

    # Analysis 1 logic here
    result_count = (
        charges_df
        .join(primary_person_df, (primary_person_df["primary_crash_id"]== charges_df["charges_crash_id"]) & (primary_person_df["primary_unit_nbr"] == charges_df["charges_unit_nbr"]), "inner")
        .filter((col("PRSN_GNDR_ID") == "Male") & (col("DEATH_CNT") > 2))
        .agg(sum(when(col("DEATH_CNT") > 2, 1).otherwise(0)).alias("Total_Count"))
    )

    # Save the result count to the specified output path
    result_count.write.parquet(output_path, mode="overwrite")

#Analysis 2
def analyze_two_wheelers_booked(spark, units_df, output_path):
    # Analysis 2 logic here
    result_count2 = (
        units_df
        .filter(col("VEH_BODY_STYL_ID").contains("MOTORCYCLE"))
        .select(sum(col("VEH_BODY_STYL_ID").contains("MOTORCYCLE").cast("int")).alias("Total_Count"))
    )

    # Save the result count to the specified output path
    result_count2.write.parquet(output_path, mode="overwrite")

#Analysis 3
def analyze_top_vehicle_makes_with_driver_death_no_airbag(spark, charges_df, primary_person_df, units_df, output_path):
    # Aliases for the columns in primary_person_df
    primary_person_df = primary_person_df.withColumnRenamed("PRSN_NBR", "primary_prsn_nbr")
    primary_person_df = primary_person_df.withColumnRenamed("CRASH_ID", "primary_crash_id")
    primary_person_df = primary_person_df.withColumnRenamed("UNIT_NBR", "primary_unit_nbr")

    # Aliases for the columns in units_df
    units_df = units_df.withColumnRenamed("CRASH_ID", "units_crash_id")
    units_df = units_df.withColumnRenamed("UNIT_NBR", "units_unit_nbr")


    # Analysis 3 logic here
    result_df = (
    primary_person_df
    .join(units_df, (primary_person_df["primary_crash_id"] == units_df["units_crash_id"]) & (primary_person_df["primary_unit_nbr"] == units_df["units_unit_nbr"]), "inner")
    .filter((col("PRSN_INJRY_SEV_ID") == "KILLED") & (col("PRSN_AIRBAG_ID") == "NOT DEPLOYED"))
    .groupBy("VEH_MAKE_ID")
    .agg(sum(when(col("PRSN_INJRY_SEV_ID") == "KILLED", 1).otherwise(0)).alias("Total_Deaths"))
    .orderBy(col("Total_Deaths").desc())
    .limit(5)  # Limit the results to the top 5 vehicle makes
    .select("VEH_MAKE_ID")  # Select only the VEH_MAKE_ID column
)

    # Save the result to the specified output path
    result_df.write.parquet(output_path, mode="overwrite")

#Analysis 4
def analyze_hit_and_run_licensed_drivers(spark, primary_person_df, charges_df, output_path):
    # Aliases for the columns in charges_df
    charges_df = charges_df.withColumnRenamed("PRSN_NBR", "charges_prsn_nbr")
    charges_df = charges_df.withColumnRenamed("CRASH_ID", "charges_crash_id")
    charges_df = charges_df.withColumnRenamed("UNIT_NBR", "charges_unit_nbr")

    # Aliases for the columns in primary_person_df
    primary_person_df = primary_person_df.withColumnRenamed("PRSN_NBR", "primary_prsn_nbr")
    primary_person_df = primary_person_df.withColumnRenamed("CRASH_ID", "primary_crash_id")
    primary_person_df = primary_person_df.withColumnRenamed("UNIT_NBR", "primary_unit_nbr")

    # Analysis 4 logic here
    result_df = (
    primary_person_df
    .filter(
        (col("PRSN_TYPE_ID") == "DRIVER") &
        ((col("DRVR_LIC_TYPE_ID") == "DRIVER LICENSE") | (col("DRVR_LIC_TYPE_ID") == "COMMERCIAL DRIVER LIC."))
    )
    .join(charges_df, (primary_person_df["primary_crash_id"]== charges_df["charges_crash_id"]) & (primary_person_df["primary_unit_nbr"] == charges_df["charges_unit_nbr"]) & (primary_person_df["primary_prsn_nbr"] == charges_df["charges_prsn_nbr"]), "inner")
    .filter(col("CHARGE").contains("HIT AND RUN"))
    .groupBy()  # Group by empty to get the count for all rows
    .agg(count("*").alias("Num_Vehicles_With_Valid_Licenses_Hit_And_Run"))
)

    # Save the result to the specified output path
    result_df.write.parquet(output_path, mode="overwrite")

#Analysis 5
def analyze_highest_accidents_without_females(spark, primary_person_df, output_path):
  # Aliases for the columns in primary_person_df
    primary_person_df = primary_person_df.withColumnRenamed("PRSN_NBR", "primary_prsn_nbr")
    primary_person_df = primary_person_df.withColumnRenamed("CRASH_ID", "primary_crash_id")
    primary_person_df = primary_person_df.withColumnRenamed("UNIT_NBR", "primary_unit_nbr")

    # Analysis 5 logic here
    result_df = (
    primary_person_df
    .filter((col("PRSN_GNDR_ID") != "FEMALE"))
    .groupBy("DRVR_LIC_STATE_ID")
    .agg(countDistinct("primary_crash_id").alias("Num_Accidents"))
    .orderBy(col("Num_Accidents").desc())
    .limit(1)
)

    # Save the result to the specified output path
    result_df.write.parquet(output_path, mode="overwrite")

#Analysis 6
def analyze_top_vehicle_makes_with_injuries(spark, units_df, output_path):
  # Define a Window specification
  window_spec = Window.orderBy(F.desc("total_count"))

  # Analysis 6 logic here
  # Calculate total_count and add a row number
  fil_result_df = (
    units_df
    .groupBy("VEH_MAKE_ID")
    .agg(
        F.sum("TOT_INJRY_CNT").alias("total_injury_count"),
        F.sum("DEATH_CNT").alias("total_death_count")
    )
    .withColumn("total_count", F.col("total_injury_count") + F.col("total_death_count"))
    .withColumn("row_num", F.row_number().over(window_spec))
)

# Filter for Top 3rd to 5th VEH_MAKE_IDs
  result_df = (
    fil_result_df
    .filter((F.col("row_num") >= 3) & (F.col("row_num") <= 5))
    .select("VEH_MAKE_ID", "total_count")
    .orderBy(F.col("row_num"))
)

  # Save the result to the specified output path
  result_df.write.parquet(output_path, mode="overwrite")

#Analysis 7
def analyze_top_ethnicity_by_vehicle_style(spark, units_df, primary_person_df, output_path):
  # Aliases for the columns in primary_person_df
  primary_person_df = primary_person_df.withColumnRenamed("PRSN_NBR", "primary_prsn_nbr")
  primary_person_df = primary_person_df.withColumnRenamed("CRASH_ID", "primary_crash_id")
  primary_person_df = primary_person_df.withColumnRenamed("UNIT_NBR", "primary_unit_nbr")

  # Aliases for the columns in units_df
  units_df = units_df.withColumnRenamed("CRASH_ID", "units_crash_id")
  units_df = units_df.withColumnRenamed("UNIT_NBR", "units_unit_nbr")

  # Analysis 7 logic here
  w = Window.partitionBy("VEH_BODY_STYL_ID").orderBy(F.col("count").desc())

  result_df = (
    units_df
    .join(primary_person_df, (primary_person_df["primary_crash_id"] == units_df["units_crash_id"]) & (primary_person_df["primary_unit_nbr"] == units_df["units_unit_nbr"]), "inner")
    .filter(~F.col("VEH_BODY_STYL_ID").isin(["NA", "UNKNOWN", "NOT REPORTED", "OTHER  (EXPLAIN IN NARRATIVE)"]))
    .filter(~F.col("PRSN_ETHNICITY_ID").isin(["NA", "UNKNOWN"]))
    .groupby("VEH_BODY_STYL_ID", "PRSN_ETHNICITY_ID")
    .count()
    .withColumn("row", F.row_number().over(w))
    .filter(F.col("row") == 1)
    .drop("row", "count")
)

  # Save the result to the specified output path
  result_df.write.parquet(output_path, mode="overwrite")

#Analysis 8
def analyze_top_zip_codes_with_alcohol_contributions(spark, units_df, primary_person_df, output_path):
  # Aliases for the columns in primary_person_df
  primary_person_df = primary_person_df.withColumnRenamed("PRSN_NBR", "primary_prsn_nbr")
  primary_person_df = primary_person_df.withColumnRenamed("CRASH_ID", "primary_crash_id")
  primary_person_df = primary_person_df.withColumnRenamed("UNIT_NBR", "primary_unit_nbr")

  # Aliases for the columns in units_df
  units_df = units_df.withColumnRenamed("CRASH_ID", "units_crash_id")
  units_df = units_df.withColumnRenamed("UNIT_NBR", "units_unit_nbr")

  # Analysis 8 logic here
  result_df = (
    units_df
    .join(primary_person_df, (primary_person_df["primary_crash_id"] == units_df["units_crash_id"]) & (primary_person_df["primary_unit_nbr"] == units_df["units_unit_nbr"]), "inner")
    .dropna(subset=["DRVR_ZIP"])
    .filter((F.col("CONTRIB_FACTR_1_ID").contains("ALCOHOL")) | (F.col("CONTRIB_FACTR_2_ID").contains("ALCOHOL")))
    .groupby("DRVR_ZIP")
    .count()
    .orderBy(F.col("count").desc())
    .limit(5).select("DRVR_ZIP")
)

  # Save the result to the specified output path
  result_df.write.parquet(output_path, mode="overwrite")

#Analysis 9
def analyze_vehicles_with_high_damages_no_property_damage(spark, damages_df, units_df, output_path):
  # Aliases for the columns in units_df
  units_df = units_df.withColumnRenamed("CRASH_ID", "units_crash_id")
  units_df = units_df.withColumnRenamed("UNIT_NBR", "units_unit_nbr")

  # Aliases for the columns in damages_df
  damages_df = damages_df.withColumnRenamed("CRASH_ID", "damages_crash_id")


  # Analysis 9 logic here
  result_df = (
    damages_df
    .join(units_df, units_df["units_crash_id"] == damages_df["damages_crash_id"], "inner")
    .filter(
        (
            (units_df.VEH_DMAG_SCL_1_ID > "DAMAGED 4") &
            (~units_df.VEH_DMAG_SCL_1_ID.isin(["NA", "NO DAMAGE", "INVALID VALUE"]))
        ) | (
            (units_df.VEH_DMAG_SCL_2_ID > "DAMAGED 4") &
            (~units_df.VEH_DMAG_SCL_2_ID.isin(["NA", "NO DAMAGE", "INVALID VALUE"]))
        )
    )
    .filter(damages_df.DAMAGED_PROPERTY == "NONE")
    .filter(units_df.FIN_RESP_TYPE_ID == "PROOF OF LIABILITY INSURANCE")
    .select("damages_crash_id")
    .distinct()
)

  # Save the result to the specified output path
  result_df.write.parquet(output_path, mode="overwrite")

#Analysis 10
def analyze_speeding_vehicles_with_top_colors_states(spark, charges_df, primary_person_df, units_df, output_path):
  # Aliases for the columns in charges_df
  charges_df = charges_df.withColumnRenamed("PRSN_NBR", "charges_prsn_nbr")
  charges_df = charges_df.withColumnRenamed("CRASH_ID", "charges_crash_id")
  charges_df = charges_df.withColumnRenamed("UNIT_NBR", "charges_unit_nbr")

  # Aliases for the columns in primary_person_df
  primary_person_df = primary_person_df.withColumnRenamed("PRSN_NBR", "primary_prsn_nbr")
  primary_person_df = primary_person_df.withColumnRenamed("CRASH_ID", "primary_crash_id")
  primary_person_df = primary_person_df.withColumnRenamed("UNIT_NBR", "primary_unit_nbr")

  # Aliases for the columns in units_df
  units_df = units_df.withColumnRenamed("CRASH_ID", "units_crash_id")
  units_df = units_df.withColumnRenamed("UNIT_NBR", "units_unit_nbr")


  # Analysis 10 logic here

  # Extract top 25 states and top 10 used vehicle colors
  top_25_state_list = [row[0] for row in units_df.filter(units_df.VEH_LIC_STATE_ID.isNotNull()).
    groupby("VEH_LIC_STATE_ID").count().
    orderBy(F.col("count").desc()).limit(25).collect()]

  top_10_used_vehicle_colors = [row[0] for row in units_df.filter(units_df.VEH_COLOR_ID != "NA").
    groupby("VEH_COLOR_ID").count().orderBy(F.col("count").desc()).limit(10).collect()]

# Perform analysis
  result_df = (
    charges_df
    .join(primary_person_df, (primary_person_df["primary_crash_id"]== charges_df["charges_crash_id"]) & (primary_person_df["primary_unit_nbr"] == charges_df["charges_unit_nbr"]), 'inner')
    .join(units_df, (primary_person_df["primary_crash_id"] == units_df["units_crash_id"]) & (primary_person_df["primary_unit_nbr"] == units_df["units_unit_nbr"]), 'inner')
    .filter(charges_df.CHARGE.contains("SPEED"))
    .filter(primary_person_df.DRVR_LIC_TYPE_ID.isin(["DRIVER LICENSE", "COMMERCIAL DRIVER LIC."]))
    .filter(units_df.VEH_COLOR_ID.isin(top_10_used_vehicle_colors))
    .filter(units_df.VEH_LIC_STATE_ID.isin(top_25_state_list))
    .groupby("VEH_MAKE_ID")
    .count()
    .orderBy(F.col("count").desc())
    .limit(5)
)

  # Save the result to the specified output path
  result_df.write.parquet(output_path, mode="overwrite")