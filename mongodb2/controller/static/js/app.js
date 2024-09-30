import Swal from 'sweetalert2'

// or via CommonJS
const Swal = require('sweetalert2')
/**
 * función que responde al evento
 * change del campo fileFoto y muestra
 * la foto seleccionada en un elemento de tipo
 * image del formulario llamado imagenProducto
 * @param {*} evento
 */
function visualizarFoto(evento){
    $fileFoto = document.querySelector('#fileFoto')
    $imagenPrevisualizacion = document.querySelector("#imagenProducto")
    const files = evento.target.files
    const archivo = files[0]
    let filename = archivo.name
    let extension = filename.split('.').pop()
    extension = extension.toLowerCase()
    if(extension !== "jpg" && extension !== "jpeg" && extension !== "png"){
        $fileFoto.value=""
        alert("La imagen debe ser en formato JPG, JPEG o PNG")    
    }else{
        const objectURL = URL.createObjectURL(archivo)
        $imagenPrevisualizacion.src = objectURL
    }
}

function visualizarModalEliminar(id) {
    Swal.fire({
        title: "¿Estás seguro de eliminar",
        showDenyButton: true,
        confirmButtonText: "Sí",
        denyButtonText: "No"
    }).then((result) => {
        /* Read more about isConfirmed, isDenied below */
        if (result.isConfirmed) {
            location.href = '/eliminar/' + id
        }
    });
}
module.exports = {visualizarFoto, visualizarModalEliminar}