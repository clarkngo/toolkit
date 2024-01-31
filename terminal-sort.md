$ cat indexes0929.txt | awk '{print $3}' | egrep "^a|^n|^c" | cut -c 1-25 | sort | uniq -c | sort | tail -n 15
     45 collect_rule_sre_v2_pla_d
     77 collect_rule_guidance_pla
     81 collect_rule_fraud_batch_
    106 collect_rule_sre_iris_pls
    218 collect_rule_sre_madcdl_r
    224 collect_rule_b_merch_time
    272 ads_cps_transaction-2023-
    272 numonitor_min_txn_agg_ext
    297 ads_shepherd_flink_sales_
    300 ads_shepherd_flink_pl_min
    305 ads_transaction_raw_data-
    365 ads_cps_transaction-2022-
    476 numonitor_min_impression_
    593 collect_rule_b_merch_les-
    706 numonitor_min_click_agg_e
