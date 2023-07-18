 python preprocess.py s2orc --input /data/users/antonkulaga/papers/s2orc/20230714_111942_00012_e64uq_061ba37d-7776-4179-ae0f-a97563a170e4 --folder /data/users/antonkulaga/papers/s2orc/pubmed/ --memory 0 # done
 python preprocess.py s2orc --input /data/users/antonkulaga/papers/s2orc/20230714_111942_00012_e64uq_0b2cf919-e7cc-4448-8df7-382006345add --folder /data/users/antonkulaga/papers/s2orc/pubmed/ --memory 0 # done
 python preprocess.py s2orc --input /data/users/antonkulaga/papers/s2orc/20230714_111942_00012_e64uq_11491525-0295-4d6d-9119-4afe180d474d --folder /data/users/antonkulaga/papers/s2orc/pubmed/ --memory 0 # done
 #now poc
 rsync --partial --progress --rsh=ssh antonkulaga@pic:/data/users/antonkulaga/papers/ /data/papers/
 python preprocess.py s2orc --input /data/papers/papers/s2orc/20230714_111942_00012_e64uq_176e01eb-8dc7-474f-bb9b-ef144daec797 --folder /data/papers/papers/s2orc/pubmed/ --memory 0
 python preprocess.py s2orc --input /data/papers/papers/s2orc/20230714_111942_00012_e64uq_17aa256c-f2c7-490e-a539-7ec5c767dd2b --folder /data/papers/papers/s2orc/pubmed/ --memory 0
 python preprocess.py s2orc --input /data/papers/papers/s2orc/20230714_111942_00012_e64uq_1945e5da-e874-4e2d-8169-a447fc56bc6d --folder /data/papers/papers/s2orc/pubmed/ --memory 0
 python preprocess.py s2orc --input /data/papers/papers/s2orc/20230714_111942_00012_e64uq_1af209fc-121b-4ee5-b539-a9aabf0ebf22 --folder /data/papers/papers/s2orc/pubmed/ --memory 0 #killed
 python preprocess.py s2orc --input /data/papers/papers/s2orc/20230714_111942_00012_e64uq_2847f4cb-dccf-4a0a-aca5-e405eb86c060 --folder /data/papers/papers/s2orc/pubmed/ --memory 0 #killed
 #now pic
 python preprocess.py s2orc --input /data/users/antonkulaga/papers/s2orc/20230714_111942_00012_e64uq_37b98fce-eec4-49e8-ab20-1f2d1421f85c --folder /data/users/antonkulaga/papers/s2orc/pubmed/ --memory 0 # four_file
 python preprocess.py s2orc --input /data/users/antonkulaga/papers/s2orc/20230714_111942_00012_e64uq_39b23e87-88e8-4273-bc47-5d6d0885f29f --folder /data/users/antonkulaga/papers/s2orc/pubmed/ --memory 0 # five_file
 python preprocess.py s2orc --input /data/users/antonkulaga/papers/s2orc/20230714_111942_00012_e64uq_41a86bf3-8d2c-44b5-a5ec-d845c5e39d88 --folder /data/users/antonkulaga/papers/s2orc/pubmed/ --memory 0 # six_file
