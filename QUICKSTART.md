# 🚀 Guía de Inicio Rápido - TTS Professional

## Instalación en 3 Pasos

### Paso 1: Preparación
```bash
# Asegúrate de tener Docker y Docker Compose instalados
docker --version
docker-compose --version
```

### Paso 2: Instalación
```bash
# Ejecuta el script de instalación automática
./start.sh install
```

Este comando:
- ✓ Verifica que Docker esté instalado
- ✓ Construye la imagen Docker
- ✓ Descarga los modelos de voz (300MB)
- ✓ Inicia la aplicación

**Tiempo estimado**: 10-15 minutos (primera vez)

### Paso 3: Acceder
Abre tu navegador en: **http://localhost:5000**

## 🎯 Primer Uso

1. **Arrastra** el archivo `ejemplo.txt` al área de carga
2. **Selecciona** género: "Voz Masculina" o "Voz Femenina"
3. **Elige** una voz específica del menú
4. **Haz clic** en "Generar Audio"
5. **Escucha** el resultado y descárgalo

## 📝 Comandos Útiles

```bash
# Iniciar la aplicación
./start.sh start

# Detener la aplicación
./start.sh stop

# Ver logs en tiempo real
./start.sh logs

# Reiniciar la aplicación
./start.sh restart

# Ver estado
./start.sh status

# Actualizar la aplicación
./start.sh update

# Ayuda
./start.sh help
```

## 🔧 Uso Manual (sin script)

```bash
# Construir
docker-compose build

# Iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

## ⚡ Características Principales

- **Offline**: Sin necesidad de internet
- **5 Voces**: Masculinas y femeninas en español
- **Velocidad**: Ajustable de 0.5x a 2.0x
- **Formatos**: .txt, .md
- **Límite**: 10,000 caracteres por síntesis
- **Audio**: Formato WAV de alta calidad

## 🎙️ Voces Disponibles

| Voz | Género | Acento | Calidad |
|-----|--------|--------|---------|
| David | Masculino | España | Alta |
| Carlos | Masculino | España | Media |
| Alejandro | Masculino | México | Alta |
| María | Femenino | España | Media |
| Claudia | Femenino | México | Premium |

## 🐛 Solución de Problemas Rápida

### Error: Puerto 5000 en uso
```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "8080:5000"  # Usa 8080 en lugar de 5000
```

### Error: Docker no está corriendo
```bash
# En Linux/Mac
sudo systemctl start docker

# En Windows
# Inicia Docker Desktop
```

### Regenerar todo desde cero
```bash
./start.sh clean  # Limpia todo
./start.sh install  # Reinstala
```

## 📊 Verificar Instalación

```bash
python3 verify.py
```

Este script verifica que todos los componentes estén correctamente instalados.

## 💡 Consejos

1. **Primera vez**: La construcción toma tiempo, ten paciencia
2. **Textos largos**: Divide en secciones de 10,000 caracteres
3. **Calidad**: Usa voces "Premium" o "Alta" para mejor resultado
4. **Velocidad**: 1.0x es natural, 1.2x es cómodo para capacitación
5. **Persistencia**: Los audios se guardan en la carpeta `outputs/`

## 🎓 Ejemplos de Uso

### Capacitación Online
1. Prepara tu material en texto
2. Divide en secciones lógicas
3. Genera audio para cada sección
4. Combina los archivos según necesites

### Presentaciones
1. Escribe el guión de narración
2. Genera audio con voz profesional
3. Descarga y añade a tus diapositivas

### E-Learning
1. Convierte documentos de estudio
2. Ofrece versión en audio a estudiantes
3. Mejora la accesibilidad del contenido

## 🔗 Recursos

- **Documentación completa**: Ver `README.md`
- **Problemas**: Revisar sección de troubleshooting
- **Logs**: `docker-compose logs -f`

## ✅ Checklist de Verificación

- [ ] Docker instalado y corriendo
- [ ] Puerto 5000 disponible
- [ ] Al menos 4GB RAM disponible
- [ ] 2GB espacio en disco
- [ ] Script ejecutado: `./start.sh install`
- [ ] Aplicación accesible en http://localhost:5000
- [ ] Audio generado correctamente

---

**¿Listo?** → Ejecuta `./start.sh install` y en 15 minutos tendrás tu conversor de texto a voz funcionando.
