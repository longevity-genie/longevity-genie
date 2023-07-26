  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_061ba37d-7776-4179-ae0f-a97563a170e4 --folder /data/papers/s2orc/pubmed/ --memory 0 # done
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_0b2cf919-e7cc-4448-8df7-382006345add --folder /data/papers/s2orc/pubmed/ --memory 0 # done
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_11491525-0295-4d6d-9119-4afe180d474d --folder /data/papers/s2orc/pubmed/ --memory 0 # done
  #now poc
  rsync --partial --progress --rsh=ssh antonkulaga@pic:/data/papers/ /data/papers/
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_176e01eb-8dc7-474f-bb9b-ef144daec797 --folder /data/papers/s2orc/pubmed/ --memory 0
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_17aa256c-f2c7-490e-a539-7ec5c767dd2b --folder /data/papers/s2orc/pubmed/ --memory 0
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_1945e5da-e874-4e2d-8169-a447fc56bc6d --folder /data/papers/s2orc/pubmed/ --memory 0
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_1af209fc-121b-4ee5-b539-a9aabf0ebf22 --folder /data/papers/s2orc/pubmed/ --memory 0 #killed
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_2847f4cb-dccf-4a0a-aca5-e405eb86c060 --folder /data/papers/s2orc/pubmed/ --memory 0 #killed
  #now pic
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_37b98fce-eec4-49e8-ab20-1f2d1421f85c --folder /data/papers/s2orc/pubmed/ --memory 0 # four_file
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_39b23e87-88e8-4273-bc47-5d6d0885f29f --folder /data/papers/s2orc/pubmed/ --memory 0 # five_file
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_41a86bf3-8d2c-44b5-a5ec-d845c5e39d88 --folder /data/papers/s2orc/pubmed/ --memory 0 # six_file
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_50ba710e-a79c-4f45-9072-1c744987d682 --folder /data/papers/s2orc/pubmed/ --memory 0 # seven_file
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_6be90075-1dfc-474c-acfe-79c1276ca297 --folder /data/papers/s2orc/pubmed/ --memory 0 # eight_file
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_6cf5d0f4-35cc-45ec-8f4a-c1f3ac258109 --folder /data/papers/s2orc/pubmed/ --memory 0 # nine_file

  #now poc
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_6f7834a8-c01d-44c0-9699-c5e5059ac6a4 --folder /data/papers/s2orc/pubmed/ --memory 0 # nine_file

  #on pic
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_77b91913-5dee-4296-a745-027a996aa2be --folder /data/papers/s2orc/pubmed/ --memory 0 # ten_file
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_87b926e2-99f6-490e-9966-c0a5d7b70fcd --folder /data/papers/s2orc/pubmed/ --memory 0

  #on poc
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_8c8564c9-376d-438e-9e07-7dcae84848c1 --folder /data/papers/s2orc/pubmed/ --memory 0 # ten
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_9710ad0e-0abb-4a1b-a8d8-2d0a927650db --folder /data/papers/s2orc/pubmed/ --memory 0 # eleven
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_a82fd724-5f8b-4dcf-9f59-d59531c59000 --folder /data/papers/s2orc/pubmed/ --memory 0 #twelve

  #on pic
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_ad89e368-674d-4fd5-aa29-4a8a0c32b545 --folder /data/papers/s2orc/pubmed/ --memory 0
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_b76c9370-94d3-43fa-8690-8d5fa592500d --folder /data/papers/s2orc/pubmed/ --memory 0
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_c3d25d47-2968-424f-b84c-b5d8683cf1bc --folder /data/papers/s2orc/pubmed/ --memory 0

  #on poc
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_c50619fc-2409-4671-ab21-78f22cc66e94 --folder /data/papers/s2orc/pubmed/ --memory 0
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_cb4cc7bf-f2bc-4916-9981-df82ab91d60e --folder /data/papers/s2orc/pubmed/ --memory 0
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_d056b2a6-d2e2-4b6a-bb25-6504e21d53ae --folder /data/papers/s2orc/pubmed/ --memory 0

  #on pic
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_d27f8a2e-7e9f-4659-8cc4-f368c7b62dbd --folder /data/papers/s2orc/pubmed/ --memory 0
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_dad816f4-cf5f-45f9-a193-b8cbc5b8c5b2 --folder /data/papers/s2orc/pubmed/ --memory 0
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_f32a21a4-6f01-4b59-95c0-7f28eb73c926 --folder /data/papers/s2orc/pubmed/ --memory 0
  python preprocess.py s2orc --input /data/papers/s2orc/20230714_111942_00012_e64uq_f32a21a4-6f01-4b59-95c0-7f28eb73c926 --folder /data/papers/s2orc/pubmed/ --memory 0
