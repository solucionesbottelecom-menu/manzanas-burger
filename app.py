import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime
import os

# CONFIGURACIÓN GENERAL
st.set_page_config(page_title="Manzanas Burger - Sistema", page_icon="🍔", layout="wide")

TU_NUMERO_WHATSAPP = "5215500000000"
DATOS_TRANSFERENCIA = """
🏦 **Banco:** BBVA / Santander
🔢 **CLABE Interbancaria:** 123456789012345678
👤 **Beneficiario:** Manzanas Burger
"""

ARCHIVO_HISTORIAL = "pedidos_registrados.csv"
ARCHIVO_INVENTARIO = "inventario_menu.csv"
CARPETA_TICKETS = "comprobantes_pago"

if not os.path.exists(CARPETA_TICKETS):
    os.makedirs(CARPETA_TICKETS)

MENU_INICIAL = [
    {
        "ID": 1,
        "Nombre": "Hamburguesa Sencilla",
        "Descripcion": "Carne clásica, pepinillos, jitomate, cebolla caramelizada, cátsup, mostaza y chiles.",
        "Precio": 85.0,
        "Stock": 20,
        "Estado": "Disponible"
    },
    {
        "ID": 2,
        "Nombre": "Hamburguesa Doble",
        "Descripcion": "Doble porción de carne, queso Oaxaca fundido, pepinillos, jitomate, cebolla caramelizada, cátsup, mostaza y chiles.",
        "Precio": 115.0,
        "Stock": 20,
        "Estado": "Disponible"
    },
    {
        "ID": 3,
        "Nombre": "Hamburguesa de Pollo",
        "Descripcion": "Filete de pollo crujiente o a la plancha, queso Oaxaca fundido, pepinillos, jitomate, cebolla caramelizada, cátsup, mostaza y chiles.",
        "Precio": 95.0,
        "Stock": 20,
        "Estado": "Disponible"
    }
]

def cargar_menu():
    if os.path.exists(ARCHIVO_INVENTARIO):
        return pd.read_csv(ARCHIVO_INVENTARIO)
    else:
        df = pd.DataFrame(MENU_INICIAL)
        df.to_csv(ARCHIVO_INVENTARIO, index=False)
        return df

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

# CONTROL DE ACCESO MEDIANTE CONTRASEÑA EN LA BARRA LATERAL
st.sidebar.title("🍔 Menú de Navegación")
opcion_vista = st.sidebar.selectbox("Selecciona la vista:", ["🛒 Vista Clientes (Hacer Pedido)", "🔐 Vista Dueño (Administración)"])

if opcion_vista == "🔐 Vista Dueño (Administración)":
    st.sidebar.markdown("---")
    password_ingresado = st.sidebar.text_input("Contraseña de Dueño:", type="password")
    # CAMBIA "tu_contraseña_segura" por la contraseña que quieras usar
    PASSWORD_CORRECTO = "123456" 
    
    if password_ingresado != PASSWORD_CORRECTO:
        modo = "Bloqueado"
        if password_ingresado != "":
            st.sidebar.error("Contraseña incorrecta")
    else:
        modo = "Dueño"
        st.sidebar.success("Acceso concedido")
else:
    modo = "Cliente"

# ==========================================
# VISTA 1: CLIENTES
# ==========================================
if modo == "Cliente":
    st.title("🍔 Manzanas Burger - Sistema de Pedidos")
    st.markdown("Elige tus hamburguesas, personaliza y selecciona tu forma de pago.")

    df_productos = cargar_menu()
    ingredientes_base = ["Pepinillos", "Jitomate", "Cebolla caramelizada", "Cátsup", "Mostaza", "Chiles"]

    st.divider()
    st.subheader("📋 Menú y Personalización")

    carrito = {}
    col_menu, col_carrito = st.columns([2, 1])

    with col_menu:
        for index, row in df_productos.iterrows():
            st.markdown(f"### {row['Nombre']}")
            st.write(f"_{row['Descripcion']}_")
            st.text(f"Precio: ${row['Precio']:.2f} MXN")
            
            # Validar si está agotado
            if row['Estado'] == "🚫 Agotado" or row['Stock'] <= 0:
                st.error("🚫 Producto Agotado temporalmente")
                st.divider()
                continue
                
            st.text(f"Disponibles: {row['Stock']}")
            
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

# ==========================================
# ESTADO BLOQUEADO (SI NO PONEN CONTRASEÑA)
# ==========================================
elif modo == "Bloqueado":
    st.title("🔒 Acceso Restringido")
    st.warning("Esta sección es exclusiva para el dueño del negocio. Por favor ingresa la contraseña correcta en la barra lateral izquierda para desbloquear el panel.")

# ==========================================
# VISTA 2: DUEÑO / ADMINISTRACIÓN
# ==========================================
elif modo == "Dueño":
    st.title("🔐 Panel de Administración - Dueño")
    st.markdown("Gestiona tus ventas, cambia el estatus de los pedidos y controla el inventario (marcar productos agotados).")

    # 1. GESTIÓN DE INVENTARIO Y DISPONIBILIDAD
    st.subheader("🍔 Control de Menú y Disponibilidad (Agotados)")
    df_menu = cargar_menu()
    
    with st.form("form_inventario"):
        st.write("Modifica el estatus o stock de las hamburguesas en tiempo real:")
        nuevos_datos = []
        for idx, row in df_menu.iterrows():
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**{row['Nombre']}**")
            with col2:
                nuevo_estado = st.selectbox("Estatus", ["Disponible", "🚫 Agotado"], index=0 if row['Estado']=="Disponible" else 1, key=f"est_{idx}")
            with col3:
                nuevo_stock = st.number_input("Stock", min_value=0, value=int(row['Stock']), key=f"stk_{idx}")
            
            nuevos_datos.append({
                "ID": row['ID'],
                "Nombre": row['Nombre'],
                "Descripcion": row['Descripcion'],
                "Precio": row['Precio'],
                "Stock": nuevo_stock,
                "Estado": nuevo_estado
            })
            st.divider()
            
        btn_actualizar_menu = st.form_submit_button("💾 Guardar Cambios en el Menú")
        if btn_actualizar_menu:
            df_updated = pd.DataFrame(nuevos_datos)
            df_updated.to_csv(ARCHIVO_INVENTARIO, index=False)
            st.success("¡Inventario y estatus actualizados correctamente!")
            st.rerun()

    st.markdown("---")
    
    # 2. CONTROL DE PEDIDOS Y VENTAS
    st.subheader("📊 Pedidos Recibidos y Ventas Totales")
    
    if os.path.exists(ARCHIVO_HISTORIAL):
        df_historial = pd.read_csv(ARCHIVO_HISTORIAL)
        
        if not df_historial.empty:
            if "Estatus" not in df_historial.columns:
                df_historial["Estatus"] = "⏳ Pendiente"
            if "ID" not in df_historial.columns:
                df_historial["ID"] = range(len(df_historial))
            if "Pago" not in df_historial.columns:
                df_historial["Pago"] = "Efectivo"
            if "Comprobante" not in df_historial.columns:
                df_historial["Comprobante"] = "Sin comprobante"
            if "Entrega" not in df_historial.columns:
                df_historial["Entrega"] = "Recoge en tienda"

            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Total de Pedidos", len(df_historial))
            with col_m2:
                pendientes_cnt = len(df_historial[df_historial['Estatus'] == "⏳ Pendiente"])
                st.metric("Pendientes", pendientes_cnt)
            with col_m3:
                st.metric("Ventas Totales", f"${df_historial['Total (MXN)'].sum():,.2f} MXN")
            
            st.divider()
            st.subheader("📋 Detalle de Pedidos y Comprobantes")
            
            for idx, row in df_historial.iterrows():
                metodo_entrega_val = row.get('Entrega', 'No especificado')
                forma_pago_val = row.get('Pago', 'Efectivo')
                
                with st.expander(f"Pedido #{row['ID']} - {row['Cliente']} (${row['Total (MXN)']} MXN) | Pago: {forma_pago_val} - [{row['Estatus']}]"):
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.write(f"**Fecha:** {row['Fecha/Hora']}")
                        st.write(f"**Método Entrega:** {metodo_entrega_val}")
                        st.write(f"**Dirección:** {row['Dirección']}")
                        st.write(f"**Forma de Pago:** {forma_pago_val}")
                    with col_info2:
                        st.write(f"**Detalle:** {row['Detalle']}")
                        
                    if forma_pago_val == "Transferencia Bancaria" and pd.notna(row['Comprobante']) and row['Comprobante'] != "Sin comprobante":
                        st.markdown("---")
                        st.write("🧾 **Comprobante de Transferencia del Cliente:**")
                        ruta_c = str(row['Comprobante'])
                        if os.path.exists(ruta_c):
                            if ruta_c.lower().endswith(('.png', '.jpg', '.jpeg')):
                                st.image(ruta_c, caption=f"Ticket de {row['Cliente']}", width=300)
                            else:
                                st.write(f"Archivo guardado en: {ruta_c}")
                        else:
                            st.warning("El archivo del comprobante no se encontró localmente.")
                    
                    st.markdown("---")
                    nuevo_estatus = st.selectbox(
                        "Actualizar Estatus:",
                        ["⏳ Pendiente", "🚴 En Camino / Salió a entrega", "✅ Entregado / Finalizado", "❌ Cancelado"],
                        index=["⏳ Pendiente", "🚴 En Camino / Salió a entrega", "✅ Entregado / Finalizado", "❌ Cancelado"].index(row['Estatus']) if row['Estatus'] in ["⏳ Pendiente", "🚴 En Camino / Salió a entrega", "✅ Entregado / Finalizado", "❌ Cancelado"] else 0,
                        key=f"status_select_{row['ID']}"
                    )
                    
                    if nuevo_estatus != row['Estatus']:
                        if st.button("💾 Guardar Cambios de Estatus", key=f"btn_save_{row['ID']}"):
                            df_historial.loc[idx, 'Estatus'] = nuevo_estatus
                            df_historial.to_csv(ARCHIVO_HISTORIAL, index=False)
                            st.success("¡Estatus actualizado correctamente!")
                            st.rerun()

            st.divider()
            st.subheader("📑 Tabla General de Historial")
            cols_a_mostrar = [c for c in ['Fecha/Hora', 'Cliente', 'Entrega', 'Dirección', 'Pago', 'Total (MXN)', 'Estatus', 'Detalle'] if c in df_historial.columns]
            st.dataframe(df_historial[cols_a_mostrar], use_container_width=True)
            
            if st.button("🗑️ Borrar Todo el Historial"):
                os.remove(ARCHIVO_HISTORIAL)
                st.rerun()
        else:
            st.info("Aún no hay pedidos registrados en el historial.")
    else:
        st.info("Aún no hay pedidos registrados.")