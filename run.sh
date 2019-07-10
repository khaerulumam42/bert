python run_squad.py --train_file dataset/tmp_train_lenna_v2.0.json \ 
 --predict_file dataset/tmp_dev_lenna_v2.0.json --do_lower_case --do_train \
 --do_predict --vocab_file wwm_uncased_L-24_H-1024_A-16/vocab.txt \ 
 --bert_config_file wwm_uncased_L-24_H-1024_A-16/bert_config.json \
 --output_dir squad_id --use_tpu --tpu_name tpuv3-big \
 --init_checkpoint wwm_uncased_L-24_H-1024_A-16/