#librerias de django rest framework
from rest_framework import serializers

#modelos de las tablas de graficas
from .models import *

#modelos de las tablas del sistema
from sistema.models import *

#calculo de la edad
from datetime import date

#manejo de expresiones regulares
import re

"""Serializer para devolver datos con los rangos de edad y el numero de alerta en ese rango"""
class edadAlertaSerializer(serializers.Serializer):
    
    mes = serializers.IntegerField()
    ano = serializers.IntegerField()

    def validate(self,data):
        #verificar que existan alerta en el mes y año proporcionados
        #en el modelo de Alerta se tiene el campo [fecha_hora]
        alertas = Alerta.objects.filter(fecha_hora__year=str(data['ano']),fecha_hora__month=str(data['mes']))
    
        if not alertas:
            raise serializers.ValidationError('No se tienen registros de este mes y año solicitado.')

        return data

    def create(self,data):
        #filtrar la alerta por el año y mes proporcionados
        
        alertas = Alerta.objects.filter(fecha_hora__year=str(data['ano']),fecha_hora__month=str(data['mes']))
        
        informacion = {}

        for alerta in alertas:
            #se busca la edad de cada usuaria que tiene la alerta 
            fecha_nacimiento = alerta.grupo.usuaria.persona.fecha_nacimiento
            edadDias = date.today() - fecha_nacimiento
            edad = edadDias.days // 365
            
            #guadar la edad y la cantidad de alertas
            if str(edad) in informacion:
                informacion[str(edad)] += 1
            else:
                informacion[str(edad)] = 1
        
        return informacion



"""Serializer para devolver el numero de alertas que se tienen en un mes"""
class numeroAlertaSerializer(serializers.Serializer):
    
    mes = serializers.IntegerField()
    ano = serializers.IntegerField()

    def validate(self,data):
        #verificar que existan alerta en el mes y año proporcionados
        #en el modelo de Alerta se tiene el campo [fecha_hora]
        alertas = Alerta.objects.filter(fecha_hora__year=str(data['ano']),fecha_hora__month=str(data['mes']))
    
        if not alertas:
            raise serializers.ValidationError('No se tienen registros de este mes y año solicitado.')

        return data

    def create(self,data):
        #buscar todas las alertas del mes brindados

        totalAlertas = Alerta.objects.filter(
            fecha_hora__year=str(data['ano']),
            fecha_hora__month=str(data['mes'])
        ).count()

        return totalAlertas



"""Serializer para devolver la frecuencia por hora de las alertas registradas en un mes"""
class horaAlertaMesSerializer(serializers.Serializer):

    mes = serializers.IntegerField()
    ano = serializers.IntegerField()

    def validate(self,data):
        #verificar que existan alertas en el mes y año proporcionados
        #en el modelo de Alerta se tiene el campo [fecha_hora]
        alertas = Alerta.objects.filter(fecha_hora__year=str(data['ano']),fecha_hora__month=str(data['mes']))
    
        if not alertas:
            raise serializers.ValidationError('No se tienen registros de este mes y año solicitado.')

        return data

    def create(self,data):
        #alertas del mes y año brindados por el usuario

        alertas = Alerta.objects.filter(fecha_hora__year=str(data['ano']),fecha_hora__month=str(data['mes']))

        informacion = {}

        for alerta in alertas:
            #hora que tiene la alerta
            hora = alerta.fecha_hora.hour

            #guardar la hora y la cantidad de las alertas
            if str(hora) in informacion:
                informacion[str(hora)] += 1
            else:
                informacion[str(hora)] = 1
    
        return informacion



"""Serializer para devolver del total de cuestionarios cuantos habian denunciado previamente"""
class denunciasPreviaSerializer(serializers.Serializer):

    ano = serializers.IntegerField()

    def validate(self,data):
        #saber si el año seleccionado tiene cuestionarios respondidos
        cuestionarios = Cuestionario.objects.filter(alerta__fecha_hora__year=data['ano'])
        if not cuestionarios:
            raise serializers.ValidationError('No se encontraron cuestionarios.')

        return data

    def create(self,data):
        #traer los cuestionarios del año solicitados por el usuario
        
        cuestionarios = Cuestionario.objects.filter(alerta__fecha_hora__year=data['ano'])
        respuestaRegex = re.compile(r'si', re.I)

        informacion = {
            'total_cuestionarios': cuestionarios.count(),
            'denuncias_previas': 0
        }

        for cuestionario in cuestionarios:
            #saber si hubo denuncia previa en este cuestionario
            hubo_denuncia = respuestaRegex.search(cuestionario.denuncia_previa)

            if hubo_denuncia != None:
                #guardar el conteo de denuncias previas
                if 'denuncias_previas' in informacion:
                    informacion['denuncias_previas'] += 1
                else:
                    informacion['denuncias_previas'] = 1

        return informacion



"""Serializer para devolver cuantas alertas al mes hay por cada nacionalidad"""
class alertasNacionalidadSerializer(serializers.Serializer):

    ano = serializers.IntegerField()
    mes = serializers.IntegerField()

    def validate(self,data):
        #buscar las alertas que tiene el mes y año brindados por el usuario
        alertas = Alerta.objects.filter(
            fecha_hora__year=data['ano'],
            fecha_hora__month=data['mes']
        )
        
        if not alertas:
            raise serializers.ValidationError('No se tienen registros de este mes y año solicitado.')

        return data

    def create(self,data):
        #buscar todas las alerta que coincidan con la fecha 
        alertas = Alerta.objects.filter(fecha_hora__year=data['ano'],fecha_hora__month=data['mes'])

        informacion = {}

        for alerta in alertas:
            #buscar la nacionalidad de cada usuaria
            pais = alerta.grupo.usuaria.pais.nombre_pais
            
            #guardar el pais y el numero de veces que se encuentran
            if str(pais) in informacion:
                informacion[str(pais)] += 1
            else:
                informacion[str(pais)] = 1

        return informacion



"""Serializer para devolver cuantas alertas al mes hay por cada tipo de complexion"""
class alertasComplexionSerializer(serializers.Serializer):

    ano = serializers.IntegerField()
    mes = serializers.IntegerField()

    def validate(self,data):
        #buscar las alertas que tiene el mes y año brindados por el usuario
        alertas = Alerta.objects.filter(
            fecha_hora__year=data['ano'],
            fecha_hora__month=data['mes']
        )
        
        if not alertas:
            raise serializers.ValidationError('No se tienen registros de este mes y año solicitado.')

        return data

    def create(self,data):
        #todas las alertas del mes
        alertas = Alerta.objects.filter(fecha_hora__year=data['ano'],fecha_hora__month=data['mes'])

        informacion = {}

        for alerta in alertas:
            #tipo de complexion de cada alerta
            tipo_complexion = alerta.grupo.usuaria.complexion.complexion

            if tipo_complexion in informacion:
                informacion[tipo_complexion] += 1
            else:
                informacion[tipo_complexion] = 1

        return informacion



"""Serializer para devolver cuantas alertas al mes hay por cada color de ojos"""
class colorOjoSerializer(serializers.Serializer):

    ano = serializers.IntegerField()
    mes = serializers.IntegerField()

    def validate(self,data):
        #alertas del mes y año que el usuario quiere visualizar
        alertas = Alerta.objects.filter(fecha_hora__year=data['ano'],fecha_hora__month=data['mes'])

        if not alertas:
            raise serializers.ValidationError('No se tienen registros de este mes y año solicitado.')

        return data

    def create(self,data):
        #alertas del año y mes  que el usuario quiere visualizar
        alertas = Alerta.objects.filter(fecha_hora__year=data['ano'],fecha_hora__month=data['mes'])

        informacion = {}

        for alerta in alertas:
            #obtener el color de ojos que tiene la usuaria
            color_ojo = alerta.grupo.usuaria.color_ojo.color_ojo

            #guardar la informacion del color de ojos y su frecuencia
            if color_ojo in informacion:
                informacion[color_ojo] += 1
            else:
                informacion[color_ojo] = 1

        return informacion



"""Serializer para delvolver cuantas alertas al mes hay por cada color de piel"""
class colorPielSerializer(serializers.Serializer):

    ano = serializers.IntegerField()
    mes = serializers.IntegerField()

    def validate(self,data):
        #validar existan alertas en el año y mes seleccionados
        alertas = Alerta.objects.filter(fecha_hora__year=data['ano'], fecha_hora__month=data['mes'])

        if not alertas:
            raise serializers.ValidationError('No se tienen registros de este mes y año solicitado.')

        return data

    def create(self,data):
        #todas las alertas
        alertas = Alerta.objects.filter(fecha_hora__year=data['ano'], fecha_hora__month=data['mes'])

        informacion = {}

        for alerta in alertas:
            #color de piel de cada usuaria
            color_piel = alerta.grupo.usuaria.color_piel.color_piel

            #guardar la informacion de cada alerta
            if color_piel in informacion:
                informacion[color_piel] += 1
            else:
                informacion[color_piel] = 1

        return informacion



"""Serializer para devolver la frecuencia por mes de las alertas en un año"""
class incidenciasTotalesSerializer(serializers.Serializer):
    ano = serializers.IntegerField()

    def validate(self,data):
        #incidencias del año solicitado
        incidencias = Alerta.objects.filter(fecha_hora__year=str(data['ano']))

        #verificar que por lo menos exista una incidencia
        if not incidencias:
            raise serializers.ValidationError('No se tienen alertas registradas en este año.')

        return data
    
    def create(self,data):
        #incidencias en el año
        incidencias = Alerta.objects.filter(fecha_hora__year=str(data['ano']))

        informacion = {
            'Enero':0,
            'Febrero':0,
            'Marzo':0,
            'Abril':0,
            'Mayo':0,
            'Junio':0,
            'Julio':0,
            'Agosto':0,
            'Septiembre':0,
            'Octubre':0,
            'Noviembre':0,
            'Diciembre':0
        }

        #guardar la informacion de cada mes
        for incidencia in incidencias:
            #mes que tiene la incidencia en numero
            mes = incidencia.fecha_hora.month

            #guardar la cantidad de incidencias
            if mes == 1:
                informacion['Enero'] += 1
            elif mes == 2:
                informacion['Febrero'] += 1
            elif mes == 3:
                informacion['Marzo'] += 1
            elif mes == 4:
                informacion['Abril'] += 1
            elif mes == 5:
                informacion['Mayo'] += 1
            elif mes == 6:
                informacion['Junio'] += 1
            elif mes == 7:
                informacion['Julio'] += 1
            elif mes == 8:
                informacion['Agosto'] += 1
            elif mes == 9:
                informacion['Septiembre'] += 1
            elif mes == 10:
                informacion['Octubre'] += 1
            elif mes == 11:
                informacion['Noviembre'] += 1
            elif mes == 1:
                informacion['Diciembre'] += 1

        return informacion



"""Serializer para devolver los puntos de incidencia por año"""
class puntosIncidenciasSerializer(serializers.Serializer):
    
    ano = serializers.IntegerField()

    def validate(self,data):
        #validar que existan alertas en el año solicitado
        alertas = Alerta.objects.filter(fecha_hora__year=str(data['ano']))

        #mensaje de error si no se tienen alertas guardadas
        if not alertas:
            raise serializers.ValidationError('No se tiene informacion de este año.')

        return data

    def create(self,data):
        #todas las alertas del año
        alertas = Alerta.objects.filter(fecha_hora__year=str(data['ano']))

        #donde se guarda la informacion
        informacion = {}
        i = 1

        for alerta in alertas:
            #primera ubicacion de cada alerta
            ubicacion = Ubicacion.objects.filter(alerta=alerta).order_by('fecha_hora').first()

            #guardar la informacion
            informacion[str(i)] = {
                'latitud' : ubicacion.latitud,
                'longitud' : ubicacion.longitud,
                'fecha_hora' : ubicacion.fecha_hora
            }

            i += 1

        return informacion