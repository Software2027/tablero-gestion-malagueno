/**
 * Gestión de evidencias multimedia para el Tablero Municipal.
 * Control estricto de límite de 40MB por archivo.
 */

const LIMITE_40MB_BYTES = 40 * 1024 * 1024; // 41,943,040 bytes

document.addEventListener('DOMContentLoaded', () => {
    const fileInputs = document.querySelectorAll('input[type="file"]');

    fileInputs.forEach(input => {
        input.addEventListener('change', () => {
            if (input.files && input.files[0]) {
                const file = input.files[0];
                if (file.size > LIMITE_40MB_BYTES) {
                    const tamanoMB = (file.size / (1024 * 1024)).toFixed(1);
                    alert(`El archivo "${file.name}" pesa ${tamanoMB} MB y supera el límite máximo permitido de 40 MB.\nPor favor seleccione un archivo más liviano o comprima el documento.`);
                    input.value = '';
                }
            }
        });
    });
});
