export default class AnimatedEllipsis extends HTMLElement {
  connectedCallback() {
    // Table id
    let forTable = this.getAttribute('for');

    // If searching inside a jQuery DataTable
    if (forTable !== null) {
      setTimeout(() => {
        let table = $(forTable).DataTable();

        let i = 0;
        this.interval = setInterval(() => {
          if (i === 3) {
            table.draw();
            i = 0;
          } else {
            let cells = table.cells()[0].filter(x => x.column === 2);

            for (let c of cells) {
              let cell = table.cell(c.row, c.column);
              if (cell.data().includes('Running')) {
                let count = cell.data().count('.');

                if (count === 3) {
                  cell.data(cell.data().slice(0, -3));
                } else {
                  cell.data(cell.data().concat('.'));
                }
              }
            }
            i++;
          }
        }, 500);
      }, 500);
    } else {
      let i = 0;
      this.interval = setInterval(() => {
        if (i++ === 3) {
          $.ajax({
            type: 'GET',
            url: window.location.href,
            data: {},
            success: (data) => {
              $('.table').html($(data).find('.table').html());
            }
          });
          i = 0;
        }

        let status = $('th:contains("Status")')[0].parentElement.children[1];
        if (status.innerHTML.includes('Running')) {
          let count = status.innerHTML.count('.');
          status.innerHTML = count === 3 ? status.innerHTML.slice(0, -3) : status.innerHTML.concat('.');
        }
      }, 500);
    }
  }

  disconnectedCallback() {
    clearInterval(this.interval);
  }
}
