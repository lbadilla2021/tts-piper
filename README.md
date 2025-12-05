# TTS Professional - Conversor de Texto a Voz Offline

Aplicación profesional de conversión de texto a voz (TTS) completamente offline, basada en Piper TTS con voces de alta calidad en español.

## 🎯 Características

- ✅ **100% Offline**: Funciona completamente sin conexión a internet
- 🎙️ **Voces Premium**: 5 voces profesionales en español (España y México)
- 👥 **Múltiples Géneros**: Voces masculinas y femeninas
- 📝 **Múltiples Formatos**: Pega texto o carga archivos .txt/.md
- ⚡ **Control de Velocidad**: Ajusta la velocidad de 0.5x a 2.0x
- 🎨 **Interfaz Moderna**: Diseño profesional y fácil de usar
- 📦 **Dockerizado**: Fácil instalación y portabilidad
- 💾 **Persistencia**: Los audios generados se guardan automáticamente

## 🔊 Voces Disponibles

### Voces Masculinas
- **David (España)** - Voz natural y clara - Calidad: Alta
- **Carlos (España)** - Voz profesional - Calidad: Media
- **Alejandro (México)** - Voz cálida y natural - Calidad: Alta

### Voces Femeninas
- **María (España)** - Voz profesional - Calidad: Media
- **Claudia (México)** - Voz premium de máxima calidad - Calidad: Premium

## 📋 Requisitos Previos

- Docker instalado (versión 20.10 o superior)
- Docker Compose (versión 1.29 o superior)
- Mínimo 4GB de RAM disponible
- 2GB de espacio en disco

## 🚀 Instalación

### Método 1: Con Docker Compose (Recomendado)

1. **Clonar o descargar el proyecto**
```bash
cd tts-app
```

2. **Construir la imagen** (este proceso descargará los modelos de voz)
```bash
docker-compose build
```
*Nota: La primera construcción puede tomar 10-15 minutos ya que descarga los modelos de voz (aproximadamente 300MB)*

3. **Iniciar la aplicación**
```bash
docker-compose up -d
```

4. **Verificar que está funcionando**
```bash
docker-compose logs -f
```

5. **Acceder a la aplicación**
Abre tu navegador en: http://localhost:5000

### Método 2: Con Docker directo

```bash
# Construir la imagen
docker build -t tts-professional .

# Ejecutar el contenedor
docker run -d \
  --name tts-app \
  -p 5000:5000 \
  -v $(pwd)/outputs:/app/outputs \
  -v $(pwd)/uploads:/app/uploads \
  tts-professional
```

## 📖 Uso

### Desde la Interfaz Web

1. **Accede a** http://localhost:5000
2. **Escribe o pega tu texto** en el área de texto (o arrastra un archivo .txt)
3. **Selecciona el género** de voz (Masculina/Femenina)
4. **Elige la voz específica** del menú desplegable
5. **Ajusta la velocidad** (opcional, por defecto 1.0x)
6. **Haz clic en "Generar Audio"**
7. **Escucha el resultado** en el reproductor integrado
8. **Descarga el archivo** haciendo clic en "Descargar Audio"

### Características Adicionales

- **Arrastrar y Soltar**: Arrastra archivos .txt directamente al área de carga
- **Control de Velocidad**: Desliza entre 0.5x (lento) y 2.0x (rápido)
- **Límites**: Máximo 10,000 caracteres por síntesis
- **Formatos Soportados**: .txt, .md

## 🗂️ Estructura del Proyecto

```
tts-app/
├── Dockerfile              # Configuración de Docker
├── docker-compose.yml      # Orquestación de Docker
├── requirements.txt        # Dependencias Python
├── download_models.py      # Script para descargar modelos de voz
├── app.py                 # Aplicación Flask principal
├── templates/
│   └── index.html         # Interfaz web
├── static/
│   ├── css/
│   │   └── styles.css     # Estilos
│   └── js/
│       └── app.js         # JavaScript
├── outputs/               # Audios generados (persistidos)
└── uploads/               # Archivos subidos (persistidos)
```

## 🔧 Comandos Útiles

### Gestión del Contenedor

```bash
# Iniciar la aplicación
docker-compose up -d

# Detener la aplicación
docker-compose down

# Ver logs en tiempo real
docker-compose logs -f

# Reiniciar la aplicación
docker-compose restart

# Ver estado
docker-compose ps
```

### Mantenimiento

```bash
# Limpiar audios generados
rm -rf outputs/*.wav

# Actualizar la aplicación
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Liberar espacio de Docker
docker system prune -a
```

## 📊 API REST (Opcional)

La aplicación también expone endpoints REST para integración:

### Sintetizar Texto
```bash
curl -X POST http://localhost:5000/api/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hola, esto es una prueba",
    "voice": "es_ES-davefx-medium",
    "speed": 1.0
  }'
```

### Obtener Voces Disponibles
```bash
curl http://localhost:5000/api/voices
```

### Subir Archivo
```bash
curl -X POST http://localhost:5000/api/upload-file \
  -F "file=@documento.txt"
```

## 🎓 Casos de Uso

- **Capacitación Online**: Convierte material de estudio en audio
- **Presentaciones**: Genera narración para diapositivas
- **Accesibilidad**: Ayuda a personas con discapacidad visual
- **E-Learning**: Crea contenido educativo en audio
- **Podcasts**: Genera episodios automatizados
- **Audiobooks**: Convierte documentos en audiolibros

## ⚙️ Configuración Avanzada

### Cambiar el Puerto

Edita `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Cambia 8080 por el puerto deseado
```

### Aumentar Límite de Caracteres

Edita `app.py`, línea ~180:
```python
if len(text) > 50000:  # Cambia este valor
```

### Agregar Más Voces

Edita `download_models.py` y agrega modelos desde:
https://github.com/rhasspy/piper/blob/master/VOICES.md

## 🐛 Solución de Problemas

### La aplicación no inicia
```bash
# Verificar logs
docker-compose logs

# Verificar puertos
lsof -i :5000
```

### Error al generar audio
- Verifica que el texto no esté vacío
- Asegúrate de haber seleccionado una voz
- Revisa los logs: `docker-compose logs -f`

### Modelos no se descargan
```bash
# Entrar al contenedor y descargar manualmente
docker-compose exec tts-app python download_models.py
```

### Problemas de permisos
```bash
# Dar permisos a los directorios
chmod -R 755 outputs uploads
```

## 🔒 Seguridad y Privacidad

- ✅ **100% Offline**: No se envían datos a servicios externos
- ✅ **Sin Telemetría**: No hay rastreo ni análisis
- ✅ **Código Abierto**: Todo el código es auditable
- ✅ **Local**: Los datos nunca salen de tu computadora

## 📝 Licencia

Este proyecto utiliza:
- **Piper TTS**: MIT License
- **Flask**: BSD License
- **Código de esta aplicación**: MIT License

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para cambios importantes:
1. Haz un fork del proyecto
2. Crea una rama para tu característica
3. Haz commit de tus cambios
4. Haz push a la rama
5. Abre un Pull Request

## 📞 Soporte

Si encuentras problemas:
1. Revisa la sección de Solución de Problemas
2. Verifica los logs: `docker-compose logs`
3. Abre un issue en el repositorio

## 🙏 Agradecimientos

- **Piper TTS** por el excelente motor de síntesis de voz
- **Rhasspy** por los modelos de voz de alta calidad
- Comunidad de código abierto

## 📈 Roadmap

- [ ] Soporte para más idiomas
- [ ] Exportación a MP3
- [ ] Procesamiento por lotes
- [ ] API GraphQL
- [ ] Personalización de voz (tono, entonación)
- [ ] Soporte para SSML
- [ ] Interfaz móvil mejorada

---

**Desarrollado para capacitación online y creación de contenido educativo en español** 🇪🇸 🇲🇽 🇨🇱
