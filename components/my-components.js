import AnimatedEllipsis from "./animated-ellipsis/animatedEllipsis";
import Range from "./range/range";

String.prototype.count = function (c) {
  let result = 0, i = 0;
  for (i; i < this.length; i++)
    if (this[i] === c)
      result++;

  return result;
};

window.addEventListener('load', () => {
  console.debug('here');
  window.customElements.define('animated-ellipsis', AnimatedEllipsis);
  window.customElements.define('range-value', Range);
});