export default class Range extends HTMLElement {
  connectedCallback() {
    this.range = M.Range.init(document.querySelectorAll("input[type=range]"));
  }

  disconnectedCallback() {
    this.range.destroy();
  }
}