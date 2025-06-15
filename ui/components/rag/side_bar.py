import streamlit as st
import requests


from services.document_services import (
    fetch_collections_raw,
    upload_document_to_collection,
    list_documents_in_collection,
    delete_collection,
    delete_document,
    create_collection
)





@st.dialog("❌ Confirmar eliminación de documento")
def confirm_delete_document_dialog(doc_name):
    st.warning(f"¿Estás seguro de que deseas eliminar el documento '{doc_name}'?")
    confirm = st.checkbox("Confirmo que deseo eliminarlo permanentemente")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancelar", use_container_width=True):
            st.session_state["doc_to_delete"] = None
            st.rerun()
    with col2:
        if st.button("Eliminar", use_container_width=True, disabled=not confirm):
            try:
                selected_col = st.session_state.get('chat_collection_select')
                if delete_document(selected_col, doc_name):
                    st.success(f"✔ Documento '{doc_name}' eliminado correctamente.")
                    st.session_state["doc_to_delete"] = None
                    st.rerun()
                else:
                    st.error("❌ No se pudo eliminar el documento.")
            except Exception as e:
                st.error(f"❌ Error: {e}")


@st.dialog("➕ Crear Nueva Colección")
def create_collection_dialog():
    st.write("Ingresa el nombre para la nueva colección:")
    new_collection_name = st.text_input("Nombre de la colección", key="dialog_collection_name")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("Crear", use_container_width=True, type="primary"):
            if not new_collection_name.strip():
                st.error("⚠️ El nombre no puede estar vacío.")
            else:
                try:
                    result = create_collection(new_collection_name.strip())
                    st.success(f"✔ Colección '{new_collection_name}' creada correctamente.")
                    st.session_state.collection_created = True
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al crear colección: {e}")


@st.dialog("❌ Eliminar Colección")
def delete_collection_dialog():
    st.write("⚠️ **Esta acción es irreversible**")
    st.write("Selecciona la colección que deseas eliminar:")

    try:
        collections_data = fetch_collections_raw()
        collection_names = [c["name"] for c in collections_data.get("collections", [])]
    except Exception as e:
        st.error("No se pudieron obtener las colecciones disponibles.")
        collection_names = []

    if collection_names:
        selected_to_delete = st.session_state.get('chat_collection_select')
        confirm = st.checkbox(
            f"⚠️ Confirmo que quiero eliminar la colección '{selected_to_delete}'",
            key="dialog_confirm_delete_col"
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Cancelar", use_container_width=True):
                st.rerun()
        with col2:
            if st.button("Eliminar", use_container_width=True, type="primary", disabled=not confirm):
                try:
                    success = delete_collection(selected_to_delete)
                    if success:
                        st.success(f"✔ Colección '{selected_to_delete}' eliminada correctamente.")
                        st.session_state.collection_deleted = True
                        st.rerun()
                    else:
                        st.warning("No se pudo eliminar la colección. Verifica permisos o estado del servidor.")
                except Exception as e:
                    st.error(f"❌ Error al eliminar colección: {e}")
    else:
        st.info("Actualmente no hay colecciones disponibles para eliminar.")
        if st.button("Cerrar", use_container_width=True):
            st.rerun()


def show_sidebar():
    st.sidebar.markdown("## Configuración del Chat")
    try:
        collections = fetch_collections_raw().get("collections", [])
        collection_names = [c["name"] for c in collections]
    except Exception as e:
        st.sidebar.error(f"Error al obtener colecciones: {e}")
        collection_names = []

    if collection_names:
        selected_collection = st.sidebar.selectbox("📚 Selecciona una colección", collection_names,
                                                   key="chat_collection_select")
        st.session_state.selected_collection = selected_collection
    else:
        st.sidebar.warning("⚠️ Debes tener al menos una colección para comenzar.")
        st.session_state.selected_collection = None

    if collection_names:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("➕ Crear", use_container_width=True):
                create_collection_dialog()
        with col2:
            if st.button("❌ Eliminar", use_container_width=True):
                delete_collection_dialog()
    else:
        if st.sidebar.button("➕ Crear", use_container_width=True):
            create_collection_dialog()

    if st.session_state.get("collection_created", False):
        st.session_state.collection_created = False
        st.rerun()
    if st.session_state.get("collection_deleted", False):
        st.session_state.collection_deleted = False
        st.rerun()

    st.sidebar.markdown("---")
    if collection_names:
        st.sidebar.markdown("## 📁 Gestión de Documentos")
        collection_name = st.session_state.get('chat_collection_select')

        if "file_uploader_key" not in st.session_state:
            st.session_state.file_uploader_key = 0

        uploaded_file = st.sidebar.file_uploader(
            "Archivo",
            type=["pdf", "docx", "md", "txt"],
            key=f"file_uploader_{st.session_state.file_uploader_key}"
        )

        if uploaded_file:
            upload_placeholder = st.sidebar.empty()
            if upload_placeholder.button("Subir documento", key="upload_button"):
                if not collection_name:
                    st.sidebar.warning("Debes introducir o seleccionar una colección.")
                else:
                    with upload_placeholder:
                        with st.spinner("Subiendo archivo..."):
                            try:
                                result = upload_document_to_collection(uploaded_file, collection_name)
                                st.sidebar.success(
                                    f"✔ Subido a '{collection_name}': {result.get('uploaded_documents', 0)} documento(s)")
                                st.session_state.file_uploader_key += 1
                                st.rerun()
                            except requests.HTTPError as http_err:
                                if http_err.response.status_code == 404:
                                    st.sidebar.error(
                                        f"❌ La colección '{collection_name}' no existe. Debes crearla primero.")
                                else:
                                    st.sidebar.error(f"❌ Error HTTP al subir el documento: {http_err}")
                            except Exception as e:
                                st.sidebar.error(f"❌ Error al subir: {e}")

        st.sidebar.markdown("## 📄 Documentos disponibles")
        try:
            documents_dict = list_documents_in_collection(collection_name)
            doc_list = documents_dict.get(collection_name, [])
        except Exception as e:
            st.sidebar.warning("No se pudieron obtener los documentos de esta colección.")
            doc_list = []

        if doc_list:
            for i, doc in enumerate(doc_list):
                cols = st.sidebar.columns([0.85, 0.15])
                with cols[0]:
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; height: 38px; overflow: hidden;">
                            <span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                {doc}
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with cols[1]:
                    if cols[1].button("❌", key=f"delete_btn_{i}", use_container_width=True):
                        st.session_state["doc_to_delete"] = doc
                        confirm_delete_document_dialog(doc)
        else:
            st.sidebar.info("Esta colección no contiene documentos.")
    else:
        st.sidebar.markdown("## 📁 Gestión de Documentos")
        st.sidebar.info("⚠️ Debes crear al menos una colección para habilitar esta sección.")


