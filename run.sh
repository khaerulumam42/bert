python run_squad.py --train_file dataset/tmp_train_lenna_v2.0.json --predict_file dataset/tmp_dev_lenna_v2.0.json --do_lower_case --do_train --do_predict --vocab_file multi_cased_L-12_H-768_A-12/vocab.txt --bert_config_file multi_cased_L-12_H-768_A-12/bert_config.json --output_dir gs://bucketcloudtputrial/squad_out --use_tpu --tpu_name tpuv3-big