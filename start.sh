#!/bin/bash

# Script de inicio rápido para TTS Professional
# Este script facilita la instalación y gestión de la aplicación

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║         TTS Professional - Setup & Manager             ║"
echo "║     Conversor de Texto a Voz Offline                   ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Función para verificar requisitos
check_requirements() {
    echo -e "${YELLOW}Verificando requisitos...${NC}"
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}✗ Docker no está instalado${NC}"
        echo "Por favor, instala Docker desde: https://docs.docker.com/get-docker/"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker instalado${NC}"
    
    # Verificar Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}✗ Docker Compose no está instalado${NC}"
        echo "Por favor, instala Docker Compose desde: https://docs.docker.com/compose/install/"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker Compose instalado${NC}"
    
    # Verificar que Docker esté corriendo
    if ! docker info &> /dev/null; then
        echo -e "${RED}✗ Docker no está corriendo${NC}"
        echo "Por favor, inicia Docker y vuelve a intentar"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker está corriendo${NC}"
    
    echo ""
}

# Función para construir la aplicación
build_app() {
    echo -e "${YELLOW}Construyendo la aplicación...${NC}"
    echo "Esto puede tomar 10-15 minutos la primera vez (descargando modelos de voz)"
    echo ""
    
    docker-compose build
    
    echo -e "${GREEN}✓ Aplicación construida exitosamente${NC}"
    echo ""
}

# Función para iniciar la aplicación
start_app() {
    echo -e "${YELLOW}Iniciando TTS Professional...${NC}"
    
    docker-compose up -d
    
    echo ""
    echo -e "${GREEN}✓ Aplicación iniciada exitosamente${NC}"
    echo ""
    echo -e "${BLUE}Accede a la aplicación en:${NC}"
    echo -e "${GREEN}http://localhost:5000${NC}"
    echo ""
    echo "Para ver los logs en tiempo real, ejecuta:"
    echo "  docker-compose logs -f"
    echo ""
}

# Función para detener la aplicación
stop_app() {
    echo -e "${YELLOW}Deteniendo TTS Professional...${NC}"
    
    docker-compose down
    
    echo -e "${GREEN}✓ Aplicación detenida${NC}"
    echo ""
}

# Función para mostrar logs
show_logs() {
    echo -e "${YELLOW}Mostrando logs (Ctrl+C para salir)...${NC}"
    echo ""
    docker-compose logs -f
}

# Función para mostrar estado
show_status() {
    echo -e "${YELLOW}Estado de la aplicación:${NC}"
    echo ""
    docker-compose ps
    echo ""
}

# Función para reiniciar la aplicación
restart_app() {
    echo -e "${YELLOW}Reiniciando TTS Professional...${NC}"
    
    docker-compose restart
    
    echo -e "${GREEN}✓ Aplicación reiniciada${NC}"
    echo ""
}

# Función para actualizar la aplicación
update_app() {
    echo -e "${YELLOW}Actualizando TTS Professional...${NC}"
    
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    
    echo -e "${GREEN}✓ Aplicación actualizada${NC}"
    echo ""
}

# Función para limpiar todo
clean_all() {
    echo -e "${RED}ADVERTENCIA: Esto eliminará todos los contenedores, imágenes y volúmenes${NC}"
    read -p "¿Estás seguro? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        docker-compose down -v
        docker system prune -a -f
        echo -e "${GREEN}✓ Limpieza completada${NC}"
    else
        echo "Limpieza cancelada"
    fi
    echo ""
}

# Función para mostrar ayuda
show_help() {
    echo "Uso: ./start.sh [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  install     - Verifica requisitos y construye la aplicación"
    echo "  start       - Inicia la aplicación"
    echo "  stop        - Detiene la aplicación"
    echo "  restart     - Reinicia la aplicación"
    echo "  logs        - Muestra los logs en tiempo real"
    echo "  status      - Muestra el estado de la aplicación"
    echo "  update      - Actualiza y reconstruye la aplicación"
    echo "  clean       - Elimina todo (contenedores, imágenes, volúmenes)"
    echo "  help        - Muestra esta ayuda"
    echo ""
    echo "Si no se proporciona ningún comando, se ejecuta la instalación completa"
    echo ""
}

# Menú principal
case "${1:-install}" in
    install)
        check_requirements
        build_app
        start_app
        ;;
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    update)
        update_app
        ;;
    clean)
        clean_all
        ;;
    help)
        show_help
        ;;
    *)
        echo -e "${RED}Comando no reconocido: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
