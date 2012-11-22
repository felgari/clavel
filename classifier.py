#! /usr/bin/env python

# Copyright (c) 2012 Felipe Gallego. All rights reserved.
#
# CLAVEL is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
This module predicts the type of variability for stars.
The variability is predicted from the light curves of the stars. This
program calculates several features from these light curves that are
used processed by means of machine learning techniques to 
The stars are retrieved from a database generated by LEMON 
(https://github.com/vterron/lemon/). 

"""

import classifargs
import classifycsv
import database
import lsproperties
import lombscargle
import periodicfeature
import nonperiodicfeature

use_star_id = 2

def print_features(perfeat, noperfeat):
    for n in range(3):
        print "-> Frecuencia fundamental %d" % n
        print "Frecuencia: %f Amplitud: %f" % (perfeat.get_fund_freq(n), perfeat.get_amplitude(n))
        print "Amplitud de los primeros armonicos: " + str(perfeat.get_amplitude_firsts_harm(n))
    
    print "Offset de las magnitudes de las frecuencias: %f" % perfeat.freq_y_offset()
    print "Diferencia de amplitudes: %f" % noperfeat.amplitude_dif()
    print "Porcentaje de puntos fuera de 1 desv. tip.: %f" % noperfeat.beyond1st()
    print "Pendiente del ajuste lineal: %f" % noperfeat.linear_trend()
    print "Maxima pendiente entre puntos del flujo: %f" % noperfeat.max_slope()
    print "Desviacion absoluta de la mediana: %f" % noperfeat.median_absolute_deviation()
    print "Porcentaje de valores alejados un 20%% de la mediana: %f" % noperfeat.median_buffer_range_percentage()
    print "Porcentaje de valores consecutivos que tienen pendiente positiva: %d" % noperfeat.pair_slope_trend()
    print "Porcentaje mayor de las diferencias entre la maxima y minima magnitud con la media: %f" % noperfeat.percent_amplitude()
    print "Diferencia en magnitudes entre el percentil 5 y el 95: %f" % noperfeat.percent_difference_flux_percentile()
    print "Sesgo (skew): %f" % noperfeat.skew()
    print "Kurtosis: %f" % noperfeat.kurtosis()
    print "Desviacion estandar: %f" % noperfeat.std()
    print "flux_percentile_ratio_mid20: %f" % noperfeat.flux_percentile_ratio_mid20()
    print "flux_percentile_ratio_mid35: %f" % noperfeat.flux_percentile_ratio_mid35()
    print "flux_percentile_ratio_mid50: %f" % noperfeat.flux_percentile_ratio_mid50()
    print "flux_percentile_ratio_mid65: %f" % noperfeat.flux_percentile_ratio_mid65()
    print "flux_percentile_ratio_mid80: %f" % noperfeat.flux_percentile_ratio_mid80()

def classify_lemon_db(filename):
    db = database.LEMONdB(filename)

    # Cambiando este valor elegimos una de las estrellas para este ejemplo
    use_star_id = 0

    # Se obtiene el id de la primera estrella
    star_id = db.star_ids[use_star_id]

    # Se obtiene la curva de la primera estrella para cada uno de los filtros.
    for pfilter in db.pfilters:
        curve = db.get_light_curve(star_id, pfilter)
        
        lsprop = lsproperties.LSProperties()

        # Se obtiene el objeto que calculara el periodograma de la curva 
        # (sin normalizar).
        ls = lombscargle.LombScargle(star_id, pfilter, curve, lsprop)

        # Se calcula el periodograma. Si se le pasa 'True como argumento, 
        # tras finalizar el calculo pinta unas graficas relativas al 
        # periodograma calculado -> ls.calculate_periodgram(True)
        pgram, nmags, ntimes = ls.calculate_periodgram()
        
        perfeat = periodicfeature.PeriodicFeature(lsprop)
        
        noperfeat = nonperiodicfeature.NonPeriodicFeature(nmags, ntimes)        

        print_features(perfeat, noperfeat)      
    
        # Si solo queremos hacerlo para el primer filtro, descomentamos 
        # el 'break', y desechamos las iteraciones sobre el resto.
        break    

def main(): 
    
    pa = classifargs.ClassifierArguments()
    
    return_value = pa.process_program_args()
    
    if return_value == pa.error_value:
        print "Error in arguments received by classifier"
    elif pa.input_file_is_cvs == True:
        ccsv = classifycsv.ClassifyCSV(pa.filename, 
                                       pa.stars_set_min_cardinal,
                                       pa.training_set_percent,
                                       pa.number_of_trees)
        
        ccsv.classify()
    else:  
        classify_lemon_db(pa.filename)

    #lee BD
    #calcula periodograma
    #calcula atributos
    #entrena
    #guarda modelo clasificador
    #evalua curvas            
    
    return return_value

if __name__ == "__main__":
    main()
    
    