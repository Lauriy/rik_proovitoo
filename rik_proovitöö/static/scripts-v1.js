document.addEventListener('DOMContentLoaded', function () {
    const addButton = document.getElementById('add-equity');
    const formsContainer = document.getElementById('equity-forms');
    const totalForms = document.getElementById('id_stakes-TOTAL_FORMS');

    addButton.addEventListener('click', function () {
        const formCount = formsContainer.children.length;
        const newForm = formsContainer.children[0].cloneNode(true);

        newForm.innerHTML = newForm.innerHTML.replace(/-0-/g, `-${formCount}-`);
        newForm.innerHTML = newForm.innerHTML.replace(/_0_/g, `_${formCount}_`);

        formsContainer.appendChild(newForm);
        totalForms.value = formCount + 1;
    });
});