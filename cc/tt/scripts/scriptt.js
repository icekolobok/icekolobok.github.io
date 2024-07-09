class MyTable extends HTMLElement {
    connectedCallback() {
        fetch('../data/crosstable.html')
            .then(response => response.text())
            .then(html => {
                this.innerHTML = html;
                this.addHighlighting();
            });
    }

    addHighlighting() {
        const table = this.querySelector('table');

        if (!table || !table.rows) {
            console.error('Table or table rows not found');
            return;
        }

        table.addEventListener('mouseover', function(e) {
            if (e.target.tagName === 'TD' || e.target.tagName === 'TH') {
                const cell = e.target;
                const row = cell.parentElement;
                const rowIndex = Array.prototype.indexOf.call(table.rows, row);
                const cellIndex = Array.prototype.indexOf.call(row.cells, cell);
                
                table.rows[rowIndex].cells[cellIndex].classList.add('highlight-transposed');

                // console.log(`Mouseover - Cell Index: ${cellIndex}, Row Index: ${rowIndex}`);

                // Highlight the row
                row.classList.add('highlight');

                // Highlight the entire column
                Array.from(table.rows).forEach((row) => {
                    if (row.cells[cellIndex]) {
                        row.cells[cellIndex].classList.add('highlight');
                    }
                });

                // Highlight the transposed cell
                if (table.rows[cellIndex] && table.rows[cellIndex].cells[rowIndex]) {
                    table.rows[cellIndex].cells[rowIndex].classList.add('highlight-transposed');
                }
            }
        });

        table.addEventListener('mouseout', function(e) {
            if (e.target.tagName === 'TD' || e.target.tagName === 'TH') {
                const cell = e.target;
                const row = cell.parentElement;
                const rowIndex = Array.prototype.indexOf.call(table.rows, row);
                const cellIndex = Array.prototype.indexOf.call(row.cells, cell);

                table.rows[rowIndex].cells[cellIndex].classList.remove('highlight-transposed');

                // console.log(`Mouseout - Cell Index: ${cellIndex}, Row Index: ${rowIndex}`);

                // Remove highlight from the row
                row.classList.remove('highlight');

                // Remove highlight from the entire column
                Array.from(table.rows).forEach((row) => {
                    if (row.cells[cellIndex]) {
                        row.cells[cellIndex].classList.remove('highlight');
                    }
                });

                // Remove highlight from the transposed cell
                if (table.rows[cellIndex] && table.rows[cellIndex].cells[rowIndex]) {
                    table.rows[cellIndex].cells[rowIndex].classList.remove('highlight-transposed');
                }
            }
        });
    }
}

customElements.define('my-table', MyTable);
