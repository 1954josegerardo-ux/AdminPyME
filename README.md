# 📦 AdminPyME - Sistema de Gestión para PYMES
## 🌐 Demo en vivo

Prueba AdminPyME sin instalar nada:

**👉 [https://apppyme-jbncydxxlcu7ue9tdq4mdu.streamlit.app](https://apppyme-jbncydxxlcu7ue9tdq4mdu.streamlit.app)**

> ℹ️ Demo pública con datos de prueba. Para uso real, descarga el código y ejecútalo localmente.

**🔐 Código de administrador por defecto:** `Admin`
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red.svg)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/SQLite-3-green.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Sistema completo de gestión empresarial diseñado para pequeñas y medianas empresas. Administra inventario, facturación, cuentas por cobrar y pagar, clientes, proveedores y reportes visuales, todo desde una interfaz web moderna y fácil de usar.

---

## 🎯 Características Principales

### 📦 Inventario
- Registro dinámico y fluido de productos
- Control de stock con alertas de mínimos
- Panel de administración protegido con código
- Borrado lógico con opción de recuperación
- Modificación de precios de compra y venta

### 🧾 Facturación
- Numeración consecutiva configurable
- Cliente existente o registro al vuelo
- Múltiples productos por factura
- Condición de pago: contado o crédito
- Ticket de venta descargable como imagen PNG
- Compatible con impresoras POS

### 💰 Cuentas por Cobrar
- Tabla interactiva de créditos pendientes
- Selección de factura con clic en fila
- Registro de abonos con método de pago
- Cancelación automática al llegar a cero
- Historial de pagos

### 🧾 Cuentas por Pagar
- Registro de compras a proveedores
- Ingreso manual del número de factura
- Actualización automática de inventario
- Abonos a deudas con proveedores
- Cancelación automática de compras

### 👥 Clientes y Proveedores
- Registro con datos fiscales
- Búsqueda inteligente
- Historial de compras

### 📈 Reportes
- Ventas por período
- Productos más vendidos
- Mejores clientes
- Estado de cuentas por cobrar/pagar
- Tendencia comparativa ventas vs compras
- Gráficos interactivos con Plotly

### ⚙️ Configuración
- Datos del negocio
- Porcentaje de impuesto
- Moneda
- Número inicial de facturación
- Código de administrador personalizable

---

## 🛠️ Tecnologías Utilizadas

| Tecnología | Uso |
|:---|:---|
| **Python 3.10+** | Lenguaje principal |
| **Streamlit** | Framework de interfaz web |
| **SQLite** | Base de datos local |
| **Pandas** | Manipulación de datos |
| **Plotly** | Gráficos interactivos |
| **Pillow** | Generación de imágenes de tickets |

---

## 🚀 Instalación

### Requisitos previos
- Python 3.10 o superior
- Navegador web (Chrome, Edge, Firefox)
- 500 MB de espacio libre

### Paso a paso

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU-USUARIO/AdminPyME.git
cd AdminPyME

# 2. Crear entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
streamlit run app.py



La aplicación se abrirá automáticamente en http://localhost:8501

⚡ Inicio Rápido
Primera configuración
Al iniciar por primera vez, ve a ⚙️ Configuración

Ingresa el código por defecto: Admin

Completa los datos de tu negocio:

Nombre, RIF, dirección, teléfono

Porcentaje de impuesto (ej: 16%)

Moneda

Número inicial de facturas

Cambia el código de administrador por uno propio

Flujo básico

1. Registrar productos → Inventario
2. Registrar clientes → Clientes (o al facturar)
3. Registrar proveedores → Cuentas por Pagar
4. Hacer compras → Cuentas por Pagar → Nueva Compra
5. Facturar ventas → Facturación → Nueva Factura
6. Cobrar créditos → Cuentas por Cobrar
7. Ver reportes → Reportes

📁 Estructura del Proyecto
AdminPyME/
├── app.py                      # Aplicación principal
├── database.py                 # Conexión y esquema SQLite
├── lanzador.py                 # Lanzador de escritorio
├── limpiar_datos.py            # Utilidad de limpieza
├── generar_datos_prueba.py     # Generador de datos de prueba
├── redondear_montos.py         # Corrector de decimales
├── requirements.txt            # Dependencias
├── README.md                   # Este archivo
├── MANUAL.md                   # Manual de usuario
├── .gitignore                  # Archivos ignorados por Git
├── modules/
│   ├── __init__.py
│   ├── inventario.py
│   ├── facturacion.py
│   ├── cobrar.py
│   ├── pagar.py
│   ├── clientes.py
│   ├── reportes.py
│   └── configuracion.py
└── .streamlit/
    └── config.toml             # Configuración de Streamlit


📖 Documentación
Manual de usuario: Ver MANUAL.md

Capturas de pantalla: Ver carpeta screenshots/ (opcional)

🔒 Seguridad
El código de administrador protege las secciones críticas

La base de datos se almacena localmente

No requiere conexión a internet

No envía datos a servidores externos

💡 Casos de Uso
Tiendas de barrio que necesitan control de inventario

Ferreterías con múltiples productos y créditos

Farmacias que manejan facturación

Distribuidoras con cuentas por cobrar y pagar

Emprendedores que quieren profesionalizar su negocio

🎓 Habilidades Demostradas
Este proyecto demuestra competencias en:

Desarrollo con Python y arquitectura modular

Streamlit a nivel profesional

Diseño de bases de datos SQLite con integridad referencial

Manipulación de datos con Pandas

Visualización con Plotly

Ingeniería de software: separación de responsabilidades, control de versiones

UX/UI: experiencia de usuario fluida e intuitiva

🔜 Roadmap
□ Sistema de usuarios con roles (admin, vendedor, cajero)
□ Empaquetado como archivo .exe
□ Códigos de barras para productos
□ Múltiples sucursales
□ Exportación de reportes a PDF y Excel
□ Integración con impresoras térmicas POS
□ Modo multi-usuario en red local
□ Respaldo automático de base de datos
🤝 Contribuciones
Las contribuciones son bienvenidas. Por favor:

Haz un fork del proyecto

Crea una rama para tu feature (git checkout -b feature/nueva-funcionalidad)

Haz commit de tus cambios (git commit -m 'Agrega nueva funcionalidad')

Haz push a la rama (git push origin feature/nueva-funcionalidad)

Abre un Pull Request

📄 Licencia
Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.

👤 Autor
[Tu Nombre Completo]

Analista y Programador

Especialista en Automatización con IA Generativa

📍 Venezuela | 🌐 Trabajo Remoto Global

📧 [tu-email@ejemplo.com]

🔗 LinkedIn

🐙 GitHub

🙏 Agradecimientos
A la comunidad de Streamlit por el excelente framework

A todos los que probaron versiones iniciales del sistema

A ti, por considerar AdminPyME para tu negocio

¿Tienes un negocio y necesitas digitalizarlo? ¿Eres desarrollador y quieres contribuir? ¡Conversemos!

⭐ Si este proyecto te resulta útil, dale una estrella en GitHub ⭐



Guarda y cierra.

---

## Parte 3: Personalizar antes de subir

Busca y cambia en el README:

1. `TU-USUARIO` → tu usuario de GitHub (`1954josegerardo-ux`)
2. `[Tu Nombre Completo]` → José Gerardo (o tu nombre completo)
3. `[tu-email@ejemplo.com]` → tu email real
4. `linkedin.com/in/tu-perfil` → tu LinkedIn

-