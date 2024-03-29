#django rest framework
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response

#django
from django.shortcuts import get_object_or_404

#serializers
from .serializers import *

#modelos
from .models import *

#permiso custom
from .permissions import *

#libreria de tiempo
from datetime import datetime


class personaViewSet(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):

    queryset = Persona.objects.all()
    serializer_class = personaSerializer
    lookup_field = 'username'


    def get_permissions(self):
        if self.action in ['login','signup','correoRecuperacion','restablecerPassword']:
            permissions = [AllowAny]
        elif self.action in ['retrieve','update','destroy','partial_update','cambiarPassword','convertirUsuaria']:
            permissions = [IsAuthenticated, IsAccountOwner]
        else:
            permissions = [IsAuthenticated]
        return [p() for p in permissions]

    @action(detail=False,methods=['POST'])
    def login(self,request):
        serializer = personaLoginSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        persona, token = serializer.save()
        data = {
            'persona' : personaSerializer(persona).data,
            'access_token' : token
        }
        return Response(data,status=status.HTTP_201_CREATED)

    @action(detail=False,methods=['POST'])
    def signup(self,request):
        serializer = personaSignupSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        persona, token = serializer.save()
        data = {
            'persona' : personaSerializer(persona).data,
            'access_token' : token
        }
        return Response(data,status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['patch'], url_path='cambiar-password')
    def cambiarPassword(self,request,*args,**kwargs):
        #parametros [password] y [password_confirmation]

        persona = get_object_or_404(Persona,email=request.user)
        self.request.data['username'] = persona.username

        serializer = cambiarPasswordSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        persona = serializer.save()

        data ={
            'persona' : personaSerializer(persona).data
        }

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False,methods=['post'], url_path='correo-recuperacion')
    def correoRecuperacion(self,request,*args,**kwargs):
        #serializer para validar el correo electronico ingresado
        serializer = personaRecuperarSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        data = 'Entra a tu correo electronico y haz clic en el enlace para restablecer tu contraseña. Podria tardar unos minutos en aparecer, asegurate de revisar tus carpetas de spam y correos no deseados.'
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False,methods=['post'], url_path='restablecer-password')
    def restablecerPassword(self,request,*args,**kwargs):
        #argumentos [token] [password] [password_confirmation]
        
        serializer = restablecerPasswordSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        persona = serializer.save()
        
        data = 'Clave de acceso cambiada con exito'

        return Response(data,status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='convertirme-usuaria')
    def convertirUsuaria(self,request,*args,**kwargs):

        persona = get_object_or_404(Persona,email=request.user)
        self.request.data['username'] = persona.username 

        serializer = convertirUsuariaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        persona = serializer.save()

        data = {
            'persona' : personaSerializer(persona).data
        }

        return Response(data, status=status.HTTP_201_CREATED)




class usuariaViewSet(viewsets.GenericViewSet):


    def get_permissions(self):
        if self.action in ['signup']:
            permissions = [AllowAny]
        elif self.action in ['informacion','borrar','actualizar']:
            permissions = [IsAuthenticated,IsAccountOwner]
        else:
            permissions = [IsAuthenticated]
        return [p() for p in permissions]

    @action(detail=False,methods=['post'])
    def signup(self,request,*args,**kwargs):
        serializer = usuariaSignupSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        persona, token = serializer.save()
        data = {
            'persona' : personaSerializer(persona).data,
            'access_token' : token
        }
        return Response(data,status=status.HTTP_201_CREATED)

    @action(detail=False,methods=['get'])
    def informacion(self,request,*args,**kwargs):
        #se obtiene la informacion desde el token de la peticion
        usuaria = get_object_or_404(Usuaria, persona = self.request.user)
        data = usuariaSerializer(usuaria).data
        return Response(data,status=status.HTTP_200_OK)

    @action(detail=False,methods=['delete'])
    def borrar(self,request):

        #obtener la instancia de la persona
        persona = get_object_or_404(Persona,email=self.request.user)
        usuaria = get_object_or_404(Usuaria, persona = persona)

        #cambiar el estado de una usuaria
        persona.is_usuaria = False
        persona.save()

        #se elimina la instancia de la usuaria
        usuaria.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,methods=['patch'])
    def actualizar(self,request,*args,**kwargs):

        #instancia de la persona
        persona = get_object_or_404(Persona,email=self.request.user)
        usuaria = get_object_or_404(Usuaria,persona=persona)
        self.request.data['username'] = persona.username

        #serializer
        serializer = usuariaActualizarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuaria = serializer.save()

        data = usuariaSerializer(usuaria).data
        
        return Response(data,status=status.HTTP_200_OK)

    @action(detail=False,methods=['delete'],url_path='borrar-enfermedad')
    def borrarEnfermedad(self,request,*args,**kwargs):
        #parametros [username] de la usuaria
        persona = get_object_or_404(Persona,email=self.request.user)
        usuaria = get_object_or_404(Usuaria,persona=persona)

        self.request.data['username']=persona.username

        #serializer
        serializer = usuariaEnfermedadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuaria = serializer.save()

        data = usuariaSerializer(usuaria).data

        return Response(data,status=status.HTTP_200_OK)




class dispositivoViewSet(viewsets.GenericViewSet):

    def get_permissions(self):
        if self.action in ['asociar','desasociar','cambiarpin','misDispositivos']:
            permissions = [IsAuthenticated,IsAccountOwner]
        else:
            permissions = [IsAuthenticated]
        return [p() for p in permissions]

    @action(detail=False,methods=['patch'])
    def asociar(self,request,*args,**kwargs):
        #parametros [numero_serie] y el [pin_desactivador] de la usuaria

        #validar que la usuaria exista dentro del sistema
        persona = get_object_or_404(Persona,email=self.request.user)
        usuaria = get_object_or_404(Usuaria, persona = persona)

        #añadir el username a los datos de request.data
        self.request.data['username'] = persona.username

        serializer = dispositivoAsociarSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        dispositivo = serializer.save()

        data = {
            'dispositivo': dispositivoInformacionSerializer(dispositivo).data
        }

        return Response(data,status = status.HTTP_200_OK)

    @action(detail=False,methods=['patch'])
    def desasociar(self,request,*args,**kwargs):
        #datos requeridos [numero_serie]

        #instancia de la usuaria
        persona = get_object_or_404(Persona,email=self.request.user)
        usuaria = get_object_or_404(Usuaria, persona = persona)

        #añadir el username de la usuaria a request.data
        self.request.data['username'] = persona.username

        serializer = dispositivoDesasociarSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save()

        return Response(status=status.HTTP_200_OK)

    @action(detail=False,methods=['patch'])
    def cambiarpin(self,request,*args,**kwargs):
        #[numero_serie] del dispositivo y el [pin_desactivador] nuevo pin

        #instancia de la usuaria
        persona = get_object_or_404(Persona,email = request.user)
        usuaria = get_object_or_404(Usuaria, persona = persona)

        #añadir a request.data el username de la usuaria
        self.request.data['username'] = persona.username

        serializer = dispositivoPinSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        dispositivo = serializer.save()

        data = {
            'dispositivo' : dispositivoInformacionSerializer(dispositivo).data
        }

        return Response(data,status=status.HTTP_200_OK)

    @action(detail=False,methods=['get'],url_path='mis-dispositivos')
    def misDispositivos(self,request,*args,**kwargs):

        #instancia de la persona
        persona = get_object_or_404(Persona,email=self.request.user)
        usuaria = get_object_or_404(Usuaria,persona=persona)

        #traer el dispositivo o dispositivos que tiene la usuaria
        try:
            dispositivos = DispositivoRastreador.objects.filter(usuaria=usuaria)
            serializer = dispositivoInformacionSerializer(dispositivos,many=True)
            data = serializer.data
            estado = status.HTTP_200_OK

        except DispositivoRastreador.DoesNotExist:
            data = None
            estado = status.HTTP_404_NOT_FOUND

        return Response(data)




class grupoViewSet(viewsets.GenericViewSet):

    def get_permissions(self):
        if self.action in ['create','retrieve','destroy','unirme','expulsar','nombre','misGrupos','salirGrupo']:
            permissions = [IsAuthenticated,IsAccountOwner]
        else:
            permissions = [IsAuthenticated]
        return [p() for p in permissions]

    def create(self,request,*args,**kwargs):
        #parametros: [nombre_grupo] del nuevo grupo

        #obtener la instancia de la usuaria
        persona = get_object_or_404(Persona,email=self.request.user)
        usuaria = get_object_or_404(Usuaria, persona = persona)

        #añadir  a request.data el username de la usuaria
        request.data['username'] = persona.username

        serializer = grupoCrearSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        grupo = serializer.save()

        data = {
            'grupo':grupoSerializer(grupo).data
        }
        return Response(data, status=status.HTTP_201_CREATED)

    def retrieve(self,request,*args,**kwargs):
        #no se necesitan ningun parametro

        persona = get_object_or_404(Persona, email = self.request.user)
        usuaria = get_object_or_404(Usuaria, persona = persona)
        grupo = get_object_or_404(Grupo, usuaria = usuaria)

        data = {
            'informacion_grupo' : grupoInformacionSerializer(grupo).data
        }

        return Response(data, status=status.HTTP_200_OK)

    def destroy(self,request,*args,**kwargs):

        persona = get_object_or_404(Persona, email = self.request.user)
        usuaria = get_object_or_404(Usuaria, persona = persona)
        grupo = get_object_or_404(Grupo, usuaria = usuaria)

        grupo.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,methods=['patch'],url_path='cambiar-nombre')
    def nombre(self,request,*args,**kwargs):
        #[nombre] nombre del grupo nuevo

        persona = get_object_or_404(Persona, email=self.request.user)
        self.request.data['username'] = persona.username

        serializer = grupoNombreSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        grupo = serializer.save()

        data = {
            'informacion_grupo' : grupoInformacionSerializer(grupo).data
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False,methods=['patch'],url_path='expulsar-miembro')
    def expulsar(self,request,*args,**kwargs):
        #parametros [username] de la persona la usuaria quiere expulsar

        persona = get_object_or_404(Persona, email=request.user)
        self.request.data['username_usuaria'] = persona.username

        serializer = grupoExpulsarSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        grupo = serializer.save()

        data = {
            'grupo': grupoInformacionSerializer(grupo).data
        }

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False,methods=['patch'])
    def unirme(self,request,*args,**kwargs):
        #parametros [clave de acceso]

        persona = get_object_or_404(Persona, email = request.user)
        self.request.data['username'] = persona.username

        serializer = grupoUnirSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        grupo = serializer.save()

        data = {
            'grupo': grupoInformacionPersonaSerializer(grupo).data
        }

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False,methods=['get'],url_path='mis-grupos')
    def misGrupos(self,request,*args,**kwargs):

        persona = get_object_or_404(Persona,email=self.request.user)

        try:
            grupos = Grupo.objects.filter(integrantes__username=persona.username)
            serializer = misGruposSerializer(grupos,many=True)
            data = serializer.data
            estado = status.HTTP_200_OK

        except Grupo.DoesNotExist:
            data = None
            estado = status.HTTP_404_NOT_FOUND

        return Response(data, status = estado)

    @action(detail=False,methods=['patch'],url_path='salir-grupo')
    def salirGrupo(self,request,*args,**kwargs):

        #obtener la instancia de la persona que saldra del grupo
        contacto = get_object_or_404(Persona,email=self.request.user)

        #obtener a la admin del grupo
        admin = get_object_or_404(Persona,username=request.data['username_usuaria'])
        usuaria = get_object_or_404(Usuaria,persona=admin)
        grupo = get_object_or_404(Grupo,usuaria = usuaria)

        #salir del grupo
        miembros = get_object_or_404(Miembros,grupo=grupo,persona=contacto)
        miembros.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)




"""cuando la alerta se produce se envia
    [numero_serie] dispositivo rastreador
    [nombre_alerta]
    [latitud]
    [longitud]
    [fecha_hora]
"""
class alertaViewSet(viewsets.GenericViewSet):

    """Los permisos de publicar y desactivar no necesitan autentificacion"""
    def get_permissions(self):
        if self.action in ['publicar','desactivacion','alternativoAlerta','alternativoDesactivacion']:
            permissions = [AllowAny]
        elif self.action in ['ultimaAlerta','trayectoria','miAlerta','desactivarAlerta']:
            permissions = [IsAuthenticated,IsAccountOwner]
        else:
            permissions = [IsAuthenticated]
        return [p() for p in permissions]

    """Publicar desde el dispositivo las ubicaciones de la alerta producida"""
    @action(detail=False, methods=['post'])
    def publicar(self,request,*args,**kwargs):

        serializer = alertaPublicarSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save()

        return Response(status=status.HTTP_200_OK)

    """El dispositivo visualiza si la alerta ha sido desactivada"""
    @action(detail=False, methods=['get'])
    def desactivacion(self,request,*args,**kwargs):

        #obtener la instancia del dispositivo rastreador
        try:
            dispositivo = get_object_or_404(DispositivoRastreador,numero_serie=request.data['numero_serie'])
            grupo = get_object_or_404(Grupo,usuaria=dispositivo.usuaria)
            serializer = grupoDesactivacionSerializer(grupo)
            data = serializer.data
            estado = status.HTTP_200_OK

        except:
            data = None
            estado = status.HTTP_404_NOT_FOUND

        return Response(data,status=estado)

    """El contacto debe de visualizar la ultima alerta de un grupo"""
    @action(detail=False,methods=['post'],url_path='ultima-alerta')
    def ultimaAlerta(self,request,*args,**kwargs):
        #parametros necesarios [username_usuaria]
        
        #instancia de la persona
        miembro = get_object_or_404(Persona,email=self.request.user)

        #instancia del grupo
        grupo = get_object_or_404(
            Grupo,
            usuaria__persona__username=self.request.data['username_usuaria'],
            estado_alerta = True    
        )
        
        #ultima alerta del grupo
        try:
            #ultima alerta del grupo al que pertenece el miembro
            alerta = Alerta.objects.filter(grupo=grupo).order_by('fecha_hora').last()
            serializer = alertaGrupoSerializer(alerta)
            data = serializer.data
            estado = status.HTTP_200_OK
        except:
            data = None
            estado = status.HTTP_404_NOT_FOUND

        return Response(data,estado)

    """El contacto visualiza la trayectoria de la alerta mas reciente"""
    @action(detail=False,methods=['post'])
    def trayectoria(self,request,*args,**kwargs):
        #parametros [username] de la usuaria que tiene la alerta activa
        #[nombre_alerta] la cual por la funcion de motificacionAlerta debe ser la ultima
        #en la PWA se debe de mostrar la ultima alerta del grupo y sus ubicaciones

        #instancia de la persona (miembro)
        miembro = get_object_or_404(Persona,email=self.request.user)

        #encontrar el grupo con la usuaria y el miembro
        grupo = get_object_or_404(
            Grupo,
            usuaria__persona__username=self.request.data['username'],
            integrantes=miembro
        )

        #alerta con el grupo y el nombre de la alerta
        alerta = get_object_or_404(
            Alerta,
            grupo=grupo,
            nombre_alerta=self.request.data['nombre_alerta']
        )

        #traer las ubicaciones de esa alerta
        ubicaciones = Ubicacion.objects.filter(alerta=alerta).order_by('fecha_hora')
        serializer = trayectoriaSerializer(ubicaciones,many=True)
        data = serializer.data

        return Response(data,status=status.HTTP_200_OK)

    """Brindar informacion de la ultima alerta a la usuaria"""
    @action(detail=False,methods=['get'],url_path='mi-alerta')
    def miAlerta(self,request,*args,**kwargs):

        #grupo de la usuaria
        grupo = get_object_or_404(
            Grupo,
            usuaria__persona__email=self.request.user,
            estado_alerta=True
        )
        
        #alerta mas reciente
        alerta = Alerta.objects.filter(grupo=grupo).order_by('fecha_hora').last()

        #informacion de la alerta
        serializer = alertaSerializer(alerta)
        data = serializer.data

        return Response(data,status=status.HTTP_200_OK)

    """Permitir a la usuaria desactivar su alerta"""
    @action(detail=False,methods=['delete'],url_path='desactivar')
    def desactivarAlerta(self, request,*args,**kwargs):
        #[nombre_alerta] que debe de ser la mas reciente
        #[pin_desactivador] que ingresa la usuaria al dispositivo

        #username de la usuaria
        usuaria = get_object_or_404(Usuaria, persona__email = self.request.user)
        self.request.data['username'] = usuaria.persona.username

        #Validar informacion
        serializer = desactivarAlertaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    """endpoint alternativo para registrar una alerta"""
    @action(detail=False,methods=['post'],url_path='publicar-alternativo')
    def alternativoAlerta(self,request,*args,**kwargs):
        
        #guardar las variables en self.data
        self.request.data['numero_serie'] = self.request.query_params.get('numero-serie',None)
        self.request.data['nombre_alerta'] = self.request.query_params.get('nombre-alerta',None)
        self.request.data['latitud'] = self.request.query_params.get('latitud',None)
        self.request.data['longitud'] = self.request.query_params.get('longitud',None)
        self.request.data['fecha_hora'] = self.request.query_params.get('fecha-hora',None)
        self.request.data['fecha_hora_inicio'] = self.request.query_params.get('fecha-hora-inicio',None)
        
        #guardar la alerta
        serializer = alertaPublicarSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        
        return Response(status=status.HTTP_200_OK)

    """endpoint alternativo para verificar si la alerta esta desactivada"""
    @action(detail=False,methods=['get'],url_path='desactivacion-alternativo')
    def alternativoDesactivacion(self,request,*args,**kwargs):
        
        #guardar la variable en self.data
        self.request.data['numero_serie'] = self.request.query_params.get('numero-serie',None)

        #obtener la instancia del dispositivo rastreador
        try:
            dispositivo = get_object_or_404(DispositivoRastreador,numero_serie=request.data['numero_serie'])
            grupo = get_object_or_404(Grupo,usuaria=dispositivo.usuaria)
            serializer = grupoDesactivacionSerializer(grupo)
            data = serializer.data
            estado = status.HTTP_200_OK
        except:
            data = None
            estado = status.HTTP_404_NOT_FOUND

        return Response(data,status=estado)




class cuestionarioViewSet(viewsets.GenericViewSet):

    """Permisos para las actividades"""
    def get_permissions(self):
        if self.action in ['create','actualizar','miCuestionario']:
            permissions = [IsAuthenticated,IsAccountOwner]
        else:
            permissions = [IsAuthenticated]
        return [p() for p in permissions]

    def create(self,request,*args,**kwargs):
        #parametro [username_usuaria] administradora del grupo
        #parametro [nombre_alerta] que debe de ser la ultima

        #instancia del miembro
        miembro = get_object_or_404(Persona,email=self.request.user)
        self.request.data['username_persona'] = miembro.username

        #serializar la informacion
        serializer = cuestionarioCrearSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cuestionario = serializer.save()

        data = {
            'cuestionario':cuestionarioSerializer(cuestionario).data
        }

        return Response(data,status=status.HTTP_201_CREATED)

    @action(detail=False,methods=['put'])
    def actualizar(self,request,*args,**kwargs):
        #[username_usuaria] administradora del grupo
        #[nombre_alerta] que se va a actualizar

        #instancia del miembro
        miembro = get_object_or_404(Persona,email=self.request.user)
        self.request.data['username_persona'] = miembro.username

        #serializer para la actualizacion
        serializer = cuestionarioActualizarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cuestionario = serializer.save()

        data = {
            'cuestionario':cuestionarioSerializer(cuestionario).data
        }

        return Response(data,status=status.HTTP_200_OK)

    @action(detail=False,methods=['post'],url_path='mi-cuestionario')
    def miCuestionario(self,request,*args,**kwargs):
        #[username_usuaria] dueña del grupo
        #[nombre_alerta]

        #instancia de la persona
        persona = get_object_or_404(Persona,email=self.request.user)
        self.request.data['username_persona'] = persona.username

        #comprobar la informacion
        serializer = miCuestionarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cuestionario = serializer.save()

        data = {
            'cuestionario':cuestionarioSerializer(cuestionario).data
        }

        return Response(data,status=status.HTTP_200_OK)




class senasViewSet(viewsets.GenericViewSet):

    """Definir los permisos"""
    def get_permissions(self):
        if self.action in ['create','retrieve','partial_update','delete']:
            permissions = [IsAuthenticated,IsAccountOwner]
        else:
            permissions = [IsAuthenticated]
        return [p() for p in permissions]

    """Registrar las señas particulares de una usuaria"""
    #salvar una seña particular a la vez
    def create(self,request,*args,**kwargs):
        #parametros [username] de la usuaria

        persona = get_object_or_404(Persona,email=self.request.user)
        self.request.data['username'] = persona.username

        serializer = senaCrearSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        sena = serializer.save()

        data = {
            'sena_particular':senaSerializer(sena).data
        }

        return Response(data,status=status.HTTP_200_OK)

    """Listar las senas particulares que tiene una usuaria"""
    def retrieve(self,request,*args,**kwargs):
        #parametros dentro de la url [username] de la usuaria

        persona = get_object_or_404(Persona,email=self.request.user)
        usuaria = get_object_or_404(Usuaria,persona=persona)

        #traer la seña o señas particulares que tiene una usuaria
        try:
            senas = UsuariaHasSenaUbicacion.objects.filter(usuaria=usuaria)
            data = {
                'senas_particulares': senaSerializer(senas,many=True).data
            }
            estado = status.HTTP_200_OK

        except UsuariaHasSenaUbicacion.DoesNotExist:
            data = None
            estado = status.HTTP_404_NOT_FOUND

        return Response(data,status=estado)

    """Borrar una sena particular que tenga la usuaria"""
    def delete(self,request,*args,**kwargs):
        #parametros [username] [descripcion] [nombre_sena_particular] [nombre_ubicacion_corporal]
        data = self.request.data

        persona = get_object_or_404(Persona,email=request.user)
        usuaria = get_object_or_404(Usuaria,persona=persona)

        # instancia de la seña particular
        sena = get_object_or_404(SenasParticulares,nombre_sena_particular=data['nombre_sena_particular'])

        # instancia de la ubicacion corporal
        ubicacion = get_object_or_404(UbicacionCorporal,nombre_ubicacion_corporal=data['nombre_ubicacion_corporal'])

        #instancia que se va a borrar
        instancia = get_object_or_404(
            UsuariaHasSenaUbicacion,
            usuaria=usuaria,
            descripcion=data['descripcion'],
            sena_particular=sena,
            ubicacion_corporal=ubicacion
        )

        #borrar la instancia
        instancia.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    """Modificar la descripcion de la seña particular"""
    def partial_update(self,request,*args,**kwargs):

        #instancia de la usuaria
        persona = get_object_or_404(Persona,email=request.user)
        self.request.data['username']=persona.username

        #serializer para actualizar la descripcion de la seña particular
        serializer = senaActualizarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sena = serializer.save()

        data = {
            'sena_particular' : senaSerializer(sena).data
        }

        return Response(data,status=status.HTTP_200_OK)



class pruebasViewSet(viewsets.GenericViewSet):
    
    """Definir permisos"""
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'], url_path='server-local-hour')
    def serverHour(self,request,*args,**kwargs):
        data = str(datetime.now())
        return Response(data,status=status.HTTP_200_OK)