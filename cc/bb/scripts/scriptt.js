// table-component.js
class MyTable extends HTMLElement {
    connectedCallback() {
        fetch('../data/crosstable.html')
            .then(response => response.text())
            .then(html => {
                this.innerHTML = html;
            });
    }
}

customElements.define('my-table', MyTable);