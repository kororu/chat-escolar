# Perfiles locales de Chat Escolar

## Dónde se guardan

Los perfiles se guardan en la tabla `profiles` de `backend/chat_escolar.db`. El navegador conserva únicamente el identificador del perfil activo y un identificador de conversación local por perfil en `localStorage`.

## Eliminar un perfil

1. En la pantalla inicial o en **Cambiar perfil**, ubica el perfil que deseas corregir.
2. Presiona **Eliminar** en esa misma tarjeta.
3. Revisa el nombre mostrado en la confirmación.
4. Selecciona **Cancelar** para no hacer cambios o **Eliminar perfil** para confirmar.

La eliminación se realiza por el ID interno del perfil, no por el nombre visible. Esto permite manejar nombres repetidos, tildes, eñes y otros caracteres Unicode de forma segura.

## Datos que se eliminan

Al confirmar, el backend elimina en una misma operación:

- el perfil seleccionado;
- todas sus entradas de historial;
- favoritos y pendientes, porque forman parte de esas entradas;
- los datos de contexto conversacional almacenados dentro de su historial.

No se elimina ningún perfil ni historial de otro `profile_id`. Actualmente no existe una tabla separada de preferencias de perfil.

En el navegador se borra también el identificador de conversación del perfil eliminado. Si era el perfil activo, se limpia el perfil activo, el último perfil usado, los mensajes y el historial visible, y se vuelve al selector. Si era el último perfil, queda disponible directamente el formulario para crear uno nuevo.

## Limitaciones

- La eliminación no tiene papelera ni recuperación automática.
- Solo se puede iniciar desde la pantalla de selección de perfiles, después de una confirmación explícita.
- No hay contraseñas ni sincronización en línea en esta etapa.

## Pruebas manuales recomendadas

1. Crea un perfil llamado `Arieñ` y otro llamado `Erik`.
2. Guarda una pregunta en ambos perfiles.
3. Presiona **Eliminar** para `Arieñ` y luego **Cancelar**: ambos perfiles deben seguir visibles.
4. Repite y confirma: debe aparecer “El perfil Arieñ fue eliminado.”
5. Verifica que el historial de `Erik` permanece disponible.
6. Selecciona un perfil, entra en **Cambiar perfil** y elimínalo: la aplicación debe volver al selector sin mantenerlo como activo.
7. Elimina el último perfil: debe aparecer solamente el formulario de creación.
