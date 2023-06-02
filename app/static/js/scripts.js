const formModule = (() => {
    let formMode = 'add';
    //CACHE DOM
    const formBackground = $(`#formBackground`)[0];
    const formContainer = $(`#formContainer`)[0];
    const exitForm = $(`#closeForm`)[0];
    const submitButton = $(`#submitButton`)[0];

    // LISTENERS
    exitForm.addEventListener(`click`, closeForm);
    formBackground.addEventListener(`click`, closeForm);

    async function showForm(mode, bookID = '') {
        submitButton.addEventListener(`click`, submitBook);
        submitButton.param = bookID;
        formMode = mode;

        if (formMode === 'add') {
            $(`#bookTitle`)[0].value = ``;
            $(`#bookAuthor`)[0].value = ``;
            $(`#coverType`)[0].value = `Paperback`;
            $(`#price`)[0].value = ``;
            $(`#availability`)[0].value = `Available`;
        }
        if (formMode === 'edit') {
            data = await ajaxModule.booksGETdetail(bookID);
            $(`#bookTitle`)[0].value = data.title;
            $(`#bookAuthor`)[0].value = data.authors.map(function (author) {
                return author['name'];
            }).join(", ");;
            $(`#coverType`)[0].value = data.paperback ? 'Paperback' : 'Hardback';
            $(`#price`)[0].value = data.price;
            $(`#availability`)[0].value = data.available;
        }
        formContainer.classList.add(`show`);
        formBackground.classList.add(`show`);
    }

    function closeForm() {
        formContainer.classList.remove(`show`);
        formBackground.classList.remove(`show`);
    }

    async function submitBook(event) {
        submitButton.removeEventListener(`click`, submitBook);
        const bookID = event.target.param;
        if (formMode === 'add') {
            if (addBookModule.invalidForm()) return;
            await ajaxModule.booksPOST();
        }
        if (formMode === 'edit') {
            await ajaxModule.booksPUT(bookID);
        }
        closeForm();
        ajaxModule.updateDisplay();
    }

    return { showForm, closeForm }
})();

const ajaxModule = (() => {

    function showSnackBar(msg) {
        const sb = $("#snackbar")[0];
        sb.innerText = msg;
        sb.className = "show";
        setTimeout(() => { sb.className = sb.className.replace("show", ""); }, 3000);
    }

    function getJsonObject() {
        return JSON.stringify({
            "title": $('#bookTitle')[0].value,
            "price": parseFloat($('#price')[0].value),
            "paperback": ($('#coverType')[0].value == "Paperback"),
            "available": $('#availability')[0].value,
            "authors": $('#bookAuthor')[0].value.replace(/,\s/g, ",").split(',')
        })
    }

    async function booksPOST() {
        const jsonFormData = getJsonObject();
        return $.ajax({
            type: 'POST',
            url: '/api/books/',
            data: jsonFormData,
            dataType: 'json',
            contentType: 'application/JSON',
            success: function () {
                showSnackBar('Book Added');
            }
        })
    }

    async function booksPUT(bookID) {
        const jsonFormData = getJsonObject();
        return $.ajax({
            type: 'PUT',
            url: `/api/books/${bookID}/`,
            data: jsonFormData,
            dataType: 'json',
            contentType: 'application/JSON',
            success: function () {
                showSnackBar('Book Updated');
            }
        })
    }

    async function booksDEL(row, bookID) {
        return $.ajax({
            type: 'DELETE',
            url: `/api/books/${bookID}/`,
            success: function () {
                $(row).remove();
                tableModule.updateLocalCopy();
                showSnackBar('Book Deleted');
            }
        })
    }

    async function booksGETdetail(bookID) {
        return $.ajax({
            method: "GET",
            url: `/api/books/${bookID}/`,
            success: function () {
                console.log(`Book ${bookID} retrieved`);
            }
        });
    }

    async function booksPurchase(bookID) {
        return $.ajax({
            method: "PUT",
            url: `/api/books/purchase/${bookID}/`,
            success: function () {
                showSnackBar('Book Purchased');
            }
        });
    }

    async function booksGET(callback) {
        mode = tableModule.getBooksMode();
        let apiUrl = "/api/books/";
        if (mode == "available") apiUrl += "available/";
        else if (mode == "unavailable") apiUrl += "unavailable/";
        else if (mode == "purchased") apiUrl += "purchased/";

        $.ajax({
            method: "GET",
            url: apiUrl,
            success: function (data) {
                callback(data)
            }
        });
    }

    function createRows(data) {
        $("tbody").empty();
        $.each(data, function (key, value) {
            const id = value.id;
            const title = value.title;
            const cover = value.paperback ? "Paperback" : "Hardback";
            const authors = value.authors.map(function (author) {
                return author['name'];
            }).join(", ");
            const price = parseFloat(value.price).toFixed(2);
            $("tbody").append(
                `<tr><td class="book-id">` + id + `</td><td>` + title + `</td><td>` + authors + `</td><td>` + cover + `</td><td>$<span>` + price + `</span></td><td class="icons-cell"><span class="material-icons-outlined sell">sell</span></td><td class="icons-cell"><span class="material-icons-outlined edit">edit</span></td><td class="icons-cell"><span class="material-icons-outlined remove">close</span></td></tr>`
            )
        })
        tableModule.updateLocalCopy();
    }

    function updateDisplay() {
        booksGET(createRows);
    }


    return { booksPOST, booksDEL, booksPUT, booksGETdetail, booksPurchase, updateDisplay }
})();

const addBookModule = (() => {
    //CACHE DOM
    const addBookButton = $(`#addBookButton`)[0];

    //LISTENERS
    addBookButton.addEventListener(`click`, () => { formModule.showForm('add') });

    // Add Book Form Validation
    function invalidForm() {
        let invalid = false;
        const invalidIndicator = document.querySelectorAll(`small`);

        for (let i = 0; i < invalidIndicator.length; i++) {
            invalidIndicator[i].classList.remove(`show`);
        }

        if (addBookForm.elements[`bookTitle`].value === ``) {
            $('#invalidTitle')[0].classList.add(`show`);
            invalid = true;
        }
        if (addBookForm.elements[`bookAuthor`].value === ``) {
            $('#invalidAuthor')[0].classList.add(`show`);
            invalid = true;
        }
        if (addBookForm.elements[`price`].value === `` || parseFloat(addBookForm.elements[`price`].value) < 0) {
            $('#invalidPrice')[0].classList.add(`show`);
            invalid = true;
        }
        return invalid;
    }

    return { invalidForm }
})();

const tableModule = (() => {
    let BOOKS_MODE = "available";
    let LOCAL_COPY = [];
    // CACHE DOM
    const bookTable = $(`#tableBody`)[0];
    const table = $(`table`)[0];
    const searchBar = $(`#searchBar`)[0];
    const bookButtons = $(`.book-status-buttons button`);

    //LISTENERS
    table.addEventListener(`click`, handleTableClick);
    Array.from(bookButtons).forEach(btn => btn.addEventListener(`click`, handleBookButtons));
    searchBar.addEventListener('input', updateTable);

    // BOOK AVAILABILITY FUNCTIONALITY
    function handleBookButtons(event) {
        if (event.target.id == "allBooks") BOOKS_MODE = "all";
        else if (event.target.id == "availableBooks") BOOKS_MODE = "available";
        else if (event.target.id == "unavailableBooks") BOOKS_MODE = "unavailable";
        else if (event.target.id == "purchasedBooks") BOOKS_MODE = "purchased";

        Array.from(bookButtons).forEach(btn => btn.classList.remove("active"));
        event.target.classList.add("active");

        ajaxModule.updateDisplay();
    }

    //TABLE FUNCTIONALITY
    function handleTableClick(event) {
        if (event.target.classList.contains(`remove`)) removeBook(event);
        else if (event.target.classList.contains(`edit`)) editBookInfo(event);
        else if (event.target.classList.contains(`sell`)) purchaseBook(event);
        else if (event.target.classList.contains(`table-header-text`)) handleSorting(event);
    }

    function findTableRow(event) {
        return event.target.parentNode.parentNode;
    }

    function findBookID(tableRow) {
        return tableRow.querySelector('.book-id').innerText;
    }

    async function removeBook(event) {
        const tableRow = findTableRow(event);
        const bookID = findBookID(tableRow);
        await ajaxModule.booksDEL(tableRow, bookID);
    }

    async function purchaseBook(event) {
        const tableRow = findTableRow(event);
        const bookID = findBookID(tableRow);
        await ajaxModule.booksPurchase(bookID);
        await ajaxModule.updateDisplay();
    }

    async function editBookInfo(event) {
        const tableRow = findTableRow(event);
        const bookID = findBookID(tableRow);
        formModule.showForm('edit', bookID);
    }

    function getBooksMode() {
        return BOOKS_MODE;
    }

    // Search Bar Functionality //
    function updateLocalCopy() {
        LOCAL_COPY = []
        Array.from(bookTable.children).forEach(row => {
            LOCAL_COPY.push(row);
        });
    }
    updateLocalCopy();

    function updateTable() {
        filteredTable = filterBooks();
        createTable(filteredTable);
    }

    function filterBooks() {
        const search = searchBar.value.toLowerCase();
        return LOCAL_COPY.filter(row => (row.children.item(1).innerText.toLowerCase().includes(search) || row.children.item(2).innerText.toLowerCase().includes(search)))
    }

    function createTable(filteredTable) {
        $("tbody").empty();
        filteredTable.forEach(row => $("tbody").append(row));
    }

    // Sorting Functionality // 
    function handleSorting(event) {
        if (event.target.innerText === ``) return;
        let filteredTable = filterBooks();
        const sortParam = getSortParameter(event);
        const sortDirection = getSortDirection(event);
        filteredTable = sortLibrary(sortDirection, sortParam, filteredTable);
        createTable(filteredTable);
    }

    function getSortParameter(event) {
        if (event.target.innerText === `Title`) return 1;
        else if (event.target.innerText === `Authors`) return 2;
        else if (event.target.innerText === `Cover`) return 3;
        else if (event.target.innerText === `Price`) return 4;
    }

    function sortLibrary(sortDirection, sortParam, filteredTable) {
        if (sortDirection === `ascending`) {
            filteredTable = filteredTable.sort(function (a, b) {
                let first, second;
                if (sortParam === 4) {
                    first = parseFloat(b.children.item(sortParam).lastElementChild.innerText);
                    second = parseFloat(a.children.item(sortParam).lastElementChild.innerText);
                } else {
                    first = b.children.item(sortParam).innerText.toString().toLowerCase();
                    second = a.children.item(sortParam).innerText.toString().toLowerCase();
                }

                if (second > first) return 1;
                else if (second === first) return 0;
                else return -1;
            });
        } else if (sortDirection === `descending`) {
            filteredTable = filteredTable.sort(function (a, b) {
                let first, second;
                if (sortParam === 4) {
                    first = parseFloat(b.children.item(sortParam).lastElementChild.innerText);
                    second = parseFloat(a.children.item(sortParam).lastElementChild.innerText);
                } else {
                    first = b.children.item(sortParam).innerText.toString().toLowerCase();
                    second = a.children.item(sortParam).innerText.toString().toLowerCase();
                }

                if (second > first) return -1;
                else if (second === first) return 0;
                else return 1;
            });
        }
        return filteredTable
    }

    function getSortDirection(event) {
        const sortArrow = event.target.parentNode.lastElementChild;
        const resetArrows = document.querySelectorAll(`.header-arrow`);

        for (let i = 0; i < resetArrows.length; i++) {
            if (sortArrow !== resetArrows[i]) {
                resetArrows[i].innerText = ``;
            }
        }

        if (sortArrow.innerText === `` || sortArrow.innerText === `expand_more`) {
            sortArrow.innerText = `expand_less`;
            return `ascending`;
        } else {
            sortArrow.innerText = `expand_more`;
            return `descending`;
        }
    }

    return { getBooksMode, updateLocalCopy }

})();
