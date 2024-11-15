document.addEventListener('DOMContentLoaded', function() {
    var roleField = document.getElementById('id_role');
    var writerFields = document.getElementById('writer-fields');

    function toggleWriterFields() {
        if (roleField.value === 'Writer') {
            writerFields.style.display = 'block';
        } else {
            writerFields.style.display = 'none';
        }
    }

    roleField.addEventListener('change', toggleWriterFields);
    toggleWriterFields();  // Call on page load
});
