#!/bin/bash
#time_series=( 'itsa4_bz-quase' 'itub4_bz-ok' 'jpm_us-ok' 'petr4_bz' 'sbsp3_bz')
time_series=('itsa4_bz' 'itub4_bz' 'jpm_us' 'petr4_bz' 'sbsp3_bz')
model_type_list=('11' '12')
filtros=('kalman')
subsets=('db' 'sym' 'coif' 'entropy') 
start=$(date +%s)

for serie_name in ${time_series[@]}
do   
   for model_type in ${model_type_list[@]}
   do
       for filtro in ${filtros[@]}
       do                                        
           for feat_subset in ${subsets[@]}
           do  
               
                partial_start=$(date +%s)
                ipython cnn_m1_multiclass_slice_metrics.ipynb $serie_name $feat_subset $model_type $filtro 
                partial_end=$(date +%s)
                echo "cnn-multiclass-$serie_name-$feat_subset-$model_type-$filtro, $(($partial_end-$partial_start))" >> m1_timecount_newlabelGA.txt
                               
           done            
       done
   done            
done

#for serie_name in ${time_series[@]}
#do   
#    for model_type in ${model_type_list[@]}
#    do
#        for filtro in ${filtros[@]}
#        do
            
#            partial_start=$(date +%s)
#            ipython mlp_m1_multiclass_slice_metrics.ipynb $serie_name $model_type $filtro 
#            partial_end=$(date +%s)
#            echo "mlp-multiclass-$serie_name-$model_type-$filtro, $(($partial_end-$partial_start))" >> m1_timecount_newlabelGA.txt
#        done
#    done
#done

#end=$(date +%s)
#echo "Total Process Time, $(($end-$start))" >> m1_timecount_americanos.txt
