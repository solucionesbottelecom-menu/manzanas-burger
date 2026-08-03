import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime
import os

st.set_page_config(page_title="Manzanas Burger - Menú", page_icon="🍔", layout="wide")

TU_NUMERO_WHATSAPP = "5215620962999"
DATOS_TRANSFERENCIA = """
🏦 **Banco:** BBVA / Santander
🔢 **CLABE Interbancaria:** 123456789012345678
👤 **Beneficiario:** Manzanas Burger
"""

ARCHIVO_HISTORIAL = "pedidos_registrados.csv"
CARPETA_TICKETS = "comprobantes_pago"

if not os.path.exists(CARPETA_TICKETS):
    os.makedirs(CARPETA_TICKETS)

def guardar_pedido(nombre, metodo_entrega, direccion, forma_pago, total, detalle, ruta_ticket="Sin comprobante"):
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nuevo_reg = {
        "ID": int(datetime.now().timestamp()),
        "Fecha/Hora": ahora,
        "Cliente": nombre,
        "Entrega": metodo_entrega,
        "Dirección": direccion if direccion else "Recoge en tienda",
        "Pago": forma_pago,
        "Total (MXN)": total,
        "Detalle": detalle,
        "Comprobante": ruta_ticket,
        "Estatus": "⏳ Pendiente"
    }
    
    if os.path.exists(ARCHIVO_HISTORIAL):
        df_hist = pd.read_csv(ARCHIVO_HISTORIAL)
        df_hist = pd.concat([df_hist, pd.DataFrame([nuevo_reg])], ignore_index=True)
    else:
        df_hist = pd.DataFrame([nuevo_reg])
        
    df_hist.to_csv(ARCHIVO_HISTORIAL, index=False)

# Vista única para el cliente (Sin pestañas de administración)
st.title("🍔 Manzanas Burger - Sistema de Pedidos")
st.markdown("Elige tus hamburguesas, personaliza y selecciona tu forma de pago.")

menu_data = [
    {
        "Nombre": "Hamburguesa Sencilla",
        "Descripcion": "Carne clásica, pepinillos, jitomate, cebolla caramelizada, cátsup, mostaza y chiles.",
        "Precio": 85.0,
        "Stock": 20
    },
    {
        "Nombre": "Hamburguesa Doble",
        "Descripcion": "Doble porción de carne, queso Oaxaca fundido, pepinillos, jitomate, cebolla caramelizada, cátsup, mostaza y chiles.",
        "Precio": 115.0,
        "Stock": 20
    },
    {
        "Nombre": "Hamburguesa de Pollo",
        "Descripcion": "Filete de pollo crujiente o a la plancha, queso Oaxaca fundido, pepinillos, jitomate, cebolla caramelizada, cátsup, mostaza y chiles.",
        "Precio": 95.0,
        "Stock": 20
    }
]

df_productos = pd.DataFrame(menu_data)
ingredientes_base = ["Pepinillos", "Jitomate", "Cebolla caramelizada", "Cátsup", "Mostaza", "Chiles"]

st.divider()
st.subheader("📋 Menú y Personalización")

carrito = {}

col_menu, col_carrito = st.columns([2, 1])

with col_menu:
    for index, row in df_productos.iterrows():
        st.markdown(f"### {row['Nombre']}")
        st.write(f"_{row['Descripcion']}_")
        st.text(f"Precio: ${row['Precio']:.2f} MXN | Disponibles: {row['Stock']}")
        
        c1, c2 = st.columns([1, 2])
        with c1:
            cantidad = st.number_input(
                "Cantidad",
                min_value=0,
                max_value=int(row['Stock']),
                value=0,
                key=f"cant_{index}"
            )
        
        modificaciones = []
        if cantidad > 0:
            with c2:
                st.markdown("**Personalizar ingredientes:**")
                ingredientes_elegidos = st.multiselect(
                    "Ingredientes:",
                    options=ingredientes_base,
                    default=ingredientes_base,
                    key=f"ing_{index}",
                    label_visibility="collapsed"
                )
                
                quitados = [ing for ing in ingredientes_base if ing not in ingredientes_elegidos]
                if quitados:
                    modificaciones.append(f"Sin {', *'.join(quitados)}")
                else:
                    modificaciones.append("Receta estándar")
                    
                extra_nota = st.text_input("Notas (ej. bien doradita):", key=f"nota_{index}", placeholder="Ej. bien doradita")
                if extra_nota:
                    modificaciones.append(f"Nota: {extra_nota}")

            carrito[row['Nombre']] = {
                "precio": row['Precio'],
                "cantidad": cantidad,
                "subtotal": row['Precio'] * cantidad,
                "modificaciones": " | ".join(modificaciones) if modificaciones else "Receta estándar"
            }
        st.divider()

# CALCULAR TOTAL GENERAL
total_general = sum(info['subtotal'] for info in carrito.values())

with col_carrito:
    st.markdown("### 🛒 Tu Carrito / Ticket")
    if len(carrito) > 0:
        for producto, info in carrito.items():
            st.markdown(f"**{info['cantidad']}x {producto}**")
            st.markdown(f"Subtotal: `${info['subtotal']:.2f} MXN`")
            if info['modificaciones']:
                st.caption(f"_{info['modificaciones']}_")
            st.markdown("---")
        st.markdown(f"### Total: ${total_general:,.2f} MXN")
    else:
        st.info("Aún no has seleccionado productos.")

# SECCIÓN DE DATOS Y PAGO
st.markdown("---")
st.subheader("📝 Datos de Envío y Forma de Pago")

mensaje_pedido = "*Nuevo Pedido - Manzanas Burger:*\n\n"
detalle_texto_admin = []
if len(carrito) > 0:
    for producto, info in carrito.items():
        subtotal = info['subtotal']
        mensaje_pedido += f"▪ {info['cantidad']}x {producto} - ${subtotal:.2f} MXN\n"
        linea_admin = f"{info['cantidad']}x {producto} (${subtotal:.2f})"
        if info['modificaciones']:
            mensaje_pedido += f"    ↳ _{info['modificaciones']}_\n"
            linea_admin += f" [{info['modificaciones']}]"
        detalle_texto_admin.append(linea_admin)
else:
    mensaje_pedido += "*(Sin productos seleccionados aún)*\n"
    
mensaje_pedido += f"\n*Total a pagar: ${total_general:.2f} MXN*\n\n"

nombre_cliente = st.text_input("Tu Nombre:", value="")
tipo_entrega = st.radio("Método de entrega:", ["Domicilio", "Recoger en tienda"])
direccion = ""
if tipo_entrega == "Domicilio":
    direccion = st.text_input("Dirección de entrega:")
    
st.markdown("### 💳 Forma de Pago")
forma_pago = st.radio("Elige cómo vas a pagar:", ["Efectivo", "Transferencia Bancaria"])

archivo_ticket = None
ruta_guardada_ticket = "Sin comprobante"

if forma_pago == "Transferencia Bancaria":
    st.info("Por favor realiza tu transferencia con los siguientes datos antes de enviar tu pedido:")
    st.markdown(DATOS_TRANSFERENCIA)
    st.markdown(f"### 💰 Total a transferir: ${total_general:,.2f} MXN")
    st.markdown("---")
    archivo_ticket = st.file_uploader("📤 Sube tu comprobante o ticket de transferencia (Imagen o PDF):", type=["png", "jpg", "jpeg", "pdf"])

if st.button("🚀 Enviar Pedido por WhatsApp", type="primary"):
    if len(carrito) == 0:
        st.warning("Selecciona al menos una hamburguesa del menú para poder hacer el pedido.")
    elif not nombre_cliente:
        st.warning("Ingresa tu nombre para continuar.")
    elif forma_pago == "Transferencia Bancaria" and archivo_ticket is None:
        st.warning("Has seleccionado Transferencia Bancaria. Por favor sube tu comprobante de pago para continuar.")
    else:
        if archivo_ticket is not None:
            timestamp_str = str(int(datetime.now().timestamp()))
            nombre_archivo_seguro = f"{timestamp_str}_{archivo_ticket.name}"
            ruta_guardada_ticket = os.path.join(CARPETA_TICKETS, nombre_archivo_seguro)
            with open(ruta_guardada_ticket, "wb") as f:
                f.write(archivo_ticket.getbuffer())
        
        detalle_completo_str = " | ".join(detalle_texto_admin)
        guardar_pedido(nombre_cliente, tipo_entrega, direccion, forma_pago, total_general, detalle_completo_str, ruta_guardada_ticket)
        
        datos_cliente = f"*Cliente:* {nombre_cliente}\n*Método de Entrega:* {tipo_entrega}\n"
        if tipo_entrega == "Domicilio":
            datos_cliente += f"*Dirección:* {direccion}\n"
        datos_cliente += f"*Forma de Pago:* {forma_pago}\n"
        if forma_pago == "Transferencia Bancaria":
            datos_cliente += f"*Comprobante:* Adjunto en sistema\n\n"
        else:
            datos_cliente += "\n"
            
        mensaje_final = mensaje_pedido + datos_cliente
        
        mensaje_codificado = urllib.parse.quote(mensaje_final)
        whatsapp_url = f"https://wa.me/{TU_NUMERO_WHATSAPP}?text={mensaje_codificado}"
        
        st.success("¡Pedido guardado correctamente!")
        st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="background-color:#25D366;color:white;padding:12px 24px;border-radius:8px;border:none;cursor:pointer;font-size:16px;font-weight:bold;">📲 Enviar Pedido por WhatsApp</button></a>', unsafe_allow_html=True)