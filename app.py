import streamlit as st
import urllib.parse
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Manzanas Burger - Menú y Pedidos",
    page_icon="🍔",
    layout="centered"
)

# Estilos CSS personalizados para un aspecto moderno tipo app de comida rápida
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #e03e3e;
        color: white;
    }
    h1, h2, h3 {
        color: #1f2937;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# BASE DE DATOS DE PRODUCTOS (MENÚ)
# ----------------------------------------------------
MENU = {
    "Hamburguesas": {
        "Manzana Clásica": {"precio": 85.0, "desc": "Carne 100% de res, queso americano, lechuga, jitomate y aderezo de la casa."},
        "Doble Carne BBQ": {"precio": 115.0, "desc": "Doble carne, doble queso, tocino crujiente y salsa BBQ ahumada."},
        "Burger Hawaiana": {"precio": 95.0, "desc": "Carne de res, jamón planchado, piña asada, queso y aderezo chipotle."},
        "Especial de la Casa": {"precio": 130.0, "desc": "Triple carne, aros de cebolla, tocino, queso cheddar fundido y aderezo especial."}
    },
    "Complementos": {
        "Papas a la Francesa": {"precio": 45.0, "desc": "Papas doraditas con sazón especial y sal de mar."},
        "Aros de Cebolla": {"precio": 50.0, "desc": "Aros crujientes acompañados de aderezo ranch."},
        "Papas con Queso y Tocino": {"precio": 75.0, "desc": "Nuestra porción de papas bañadas en queso cheddar y trocitos de tocino."}
    },
    "Bebidas": {
        "Refresco de Lata (355ml)": {"precio": 25.0, "desc": "Coca-Cola, Manzana, Sprite o Fanta."},
        "Agua de Sabor del Día (1L)": {"precio": 35.0, "desc": "Horchata o Jamaica natural fresca."},
        "Malteada de Chocolate o Fresa": {"precio": 55.0, "desc": "Preparada con helado artesanal y crema batida."}
    }
}

# ----------------------------------------------------
# CONFIGURACIÓN DE PEDIDOS (Simulación en sesión)
# ----------------------------------------------------
if 'pedidos_realizados' not in st.session_state:
    st.session_state.pedidos_realizados = []

# ----------------------------------------------------
# BARRA LATERAL (MENÚ DE NAVEGACIÓN Y ACCESO DUEÑO)
# ----------------------------------------------------
st.sidebar.title("🍔 Manzanas Burger")
st.sidebar.markdown("---")

# Opciones visibles para todo el público
modo = st.sidebar.radio("Navegación", ["📝 Hacer Pedido", "🔐 Sección Dueño (Admin)"])

# ----------------------------------------------------
# VISTA 1: HACER PEDIDO (CLIENTES)
# ----------------------------------------------------
if modo == "📝 Hacer Pedido":
    st.title("🍔 Manzanas Burger")
    st.markdown("¡Bienvenido! Arma tu pedido seleccionando tus productos favoritos y te lo enviamos directo por WhatsApp.")
    st.markdown("---")

    carrito = {}

    for categoria, items in MENU.items():
        st.subheader(f"📌 {categoria}")
        for plato, info in items.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{plato}** — *${info['precio']:.2f}*")
                st.caption(info['desc'])
            with col2:
                cantidad = st.number_input(f"Cant", min_value=0, max_value=10, value=0, key=f"{categoria}_{plato}", label_visibility="collapsed")
                if cantidad > 0:
                    carrito[plato] = {"precio": info['precio'], "cantidad": cantidad}
        st.markdown("")

    st.markdown("---")
    st.subheader("📋 Resumen y Datos de Entrega")

    if carrito:
        total_pedido = 0
        st.markdown("**Productos seleccionados:**")
        for item, detalles in carrito.items():
            sub = detalles['precio'] * detalles['cantidad']
            total_pedido += sub
            st.write(f"- {detalles['cantidad']}x {item} = ${sub:.2f}")
        
        st.markdown(f"### **Total a Pagar: ${total_pedido:.2f}**")
        st.markdown("---")

        with st.form("form_pedido"):
            st.markdown("**Datos para tu envío o entrega:**")
            nombre_cliente = st.text_input("Nombre completo:")
            telefono_cliente = st.text_input("Teléfono de contacto:")
            tipo_entrega = st.radio("Tipo de servicio:", ["🛵 Entrega a Domicilio", "🏃‍♂️ Pasar a recoger (Llevar)"])
            
            direccion = ""
            if tipo_entrega == "🛵 Entrega a Domicilio":
                direccion = st.text_area("Dirección exacta (Calle, Colonia, Referencias):")
            
            comentarios = st.text_area("Comentarios adicionales (ej. sin cebolla, salsa aparte):")

            enviar = st.form_submit_button("🚀 Enviar Pedido por WhatsApp")

            if enviar:
                if not nombre_cliente or not telefono_cliente:
                    st.error("Por favor, ingresa al menos tu Nombre y Teléfono.")
                elif tipo_entrega == "🛵 Entrega a Domicilio" and not direccion:
                    st.error("Por favor, ingresa tu dirección para el envío a domicilio.")
                else:
                    # Armar texto para WhatsApp
                    mensaje = f"*¡NUEVO PEDIDO DE MANZANAS BURGER!* 🍔\n\n"
                    mensaje += f"*Cliente:* {nombre_cliente}\n"
                    mensaje += f"*Teléfono:* {telefono_cliente}\n"
                    mensaje += f"*Tipo:* {tipo_entrega}\n"
                    if tipo_entrega == "🛵 Entrega a Domicilio":
                        mensaje += f"*Dirección:* {direccion}\n"
                    if comentarios:
                        mensaje += f"*Notas:* {comentarios}\n"
                    
                    mensaje += "\n*Detalle del pedido:*\n"
                    for item, detalles in carrito.items():
                        sub = detalles['precio'] * detalles['cantidad']
                        mensaje += f"• {detalles['cantidad']}x {item} (${sub:.2f})\n"
                    
                    mensaje += f"\n*TOTAL: ${total_pedido:.2f}*"

                    # Guardar en la sesión de pedidos del negocio
                    nuevo_registro = {
                        "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "cliente": nombre_cliente,
                        "telefono": telefono_cliente,
                        "total": total_pedido,
                        "tipo": tipo_entrega
                    }
                    st.session_state.pedidos_realizados.append(nuevo_registro)

                    # Codificar URL para WhatsApp (Tu número actual configurado)
                    # NOTA: Puedes cambiar este número de WhatsApp cuando lo necesites
                    numero_negocio = "5215500000000" # Reemplaza con tu número personal o de negocio con lada 521
                    url_whatsapp = f"https://wa.me/{numero_negocio}?text={urllib.parse.quote(mensaje)}"

                    st.success("¡Pedido generado con éxito! Redirigiendo a WhatsApp...")
                    st.markdown(f'<meta http-equiv="refresh" content="0;url={url_whatsapp}">', unsafe_allow_html=True)
                    st.markdown(f"Si no se abre automáticamente, [haz clic aquí para enviar tu pedido]({url_whatsapp})", unsafe_allow_html=True)
    else:
        st.info("👆 Selecciona al menos un producto de la lista para armar tu pedido.")

# ----------------------------------------------------
# VISTA 2: SECCIÓN DUEÑO / ADMINISTRACIÓN (PROTEGIDA POR PIN)
# ----------------------------------------------------
elif modo == "🔐 Sección Dueño (Admin)":
    st.title("🔐 Panel de Administración")
    st.markdown("Área exclusiva para el control de ventas y pedidos del negocio.")
    st.markdown("---")

    # PIN de 6 dígitos predeterminado (puedes cambiarlo aquí mismo si deseas)
    PIN_CORRECTO = "123456"

    pin_ingresado = st.sidebar.text_input("Ingresa PIN de Dueño (6 dígitos):", type="password", max_chars=6)

    if pin_ingresado == PIN_CORRECTO:
        st.sidebar.success("¡Acceso concedido!")
        st.markdown("### 📊 Resumen General del Negocio")

        # Opción para esconder el total vendido
        esconder_total = st.checkbox("👁️ Ocultar montos y total vendido en pantalla", value=False)

        total_ventas_acumulado = sum([p['total'] for p in st.session_state.pedidos_realizados])
        total_pedidos_cuenta = len(st.session_state.pedidos_realizados)

        col1, col2 = st.columns(2)
        with col1:
            if esconder_total:
                st.metric(label="Total Vendido", value="$ ••••••")
            else:
                st.metric(label="Total Vendido", value=f"${total_ventas_acumulado:.2f}")
        with col2:
            st.metric(label="Pedidos Totales", value=total_pedidos_cuenta)

        st.markdown("---")
        st.subheader("📜 Historial de Pedidos Recientes")

        if st.session_state.pedidos_realizados:
            for idx, p in enumerate(reversed(st.session_state.pedidos_realizados), 1):
                with st.expander(f"Pedido #{total_pedidos_cuenta - idx + 1} - {p['cliente']} ({p['hora']})"):
                    st.write(f"**Teléfono:** {p['telefono']}")
                    st.write(f"**Tipo:** {p['tipo']}")
                    if esconder_total:
                        st.write(f"**Total:** $ ••••••")
                    else:
                        st.write(f"**Total:** ${p['total']:.2f}")
        else:
            st.info("Aún no hay registros de pedidos en esta sesión.")
            
    elif pin_ingresado == "":
        st.warning("⚠️ Por favor, introduce tu PIN de 6 dígitos en la barra lateral para acceder al panel de administración.")
    else:
        st.sidebar.error("❌ PIN incorrecto. Inténtalo de nuevo.")
        st.error("Acceso denegado. Introduce el PIN correcto en la barra lateral.")