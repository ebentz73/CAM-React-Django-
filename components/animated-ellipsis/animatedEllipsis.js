export default class AnimatedEllipsis extends HTMLElement {
  connectedCallback() {
    // Table id
    let forTable = this.getAttribute('for');

    // If searching inside a jQuery DataTable
    if (forTable !== null) {
      setTimeout(() => {
        let table = $(forTable).DataTable({destroy: true});

        let cells = table.cells()[0].filter(x => {
          return table.cell(x.row, x.column).data().includes('...');
        });

        this.interval = setInterval(() => {
          cells.forEach((x) => {
            let cell = table.cell(x.row, x.column);
            let count = cell.data().count('.');
            cell.data(count === 3 ? cell.data().slice(0, -3) : cell.data().concat('.'));
          });
        }, 500);
      }, 500);
    } else {
      let tds = $('td:contains("...")');

      // Animate the ellipsis every half second
      this.interval = setInterval(() => {
        tds.each((index) => {
          let td = tds.get(index);
          let count = td.innerHTML.count('.');
          td.innerHTML = count === 3 ? td.innerHTML.slice(0, -3) : td.innerHTML.concat('.');
        });
      }, 500);
    }
  }

  disconnectedCallback() {
    clearInterval(this.interval);
  }
}
