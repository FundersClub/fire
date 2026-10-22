import 'core-js/es6';
import 'core-js/es7/reflect';
import 'hammerjs/hammer';
import 'normalize.css/normalize.css';
import './static/css/component-overrides.css';
require('zone.js/dist/zone');

// Promise.prototype.finally, installed on zone.js's Promise. Inlined rather than
// using the promise.prototype.finally package: its unpinned es-abstract deps now
// ship ES2017 syntax that the build's UglifyJS (ES5-only) cannot parse.
if (typeof Promise.prototype['finally'] !== 'function') {
    Promise.prototype['finally'] = function (onFinally: () => any) {
        const P = this.constructor;
        return this.then(
            (value: any) => P.resolve(onFinally()).then(() => value),
            (reason: any) => P.resolve(onFinally()).then(() => { throw reason; })
        );
    };
}

if (process.env.ENV === 'production') {
    // Production
} else {
    // Development and test
    Error['stackTraceLimit'] = Infinity;
    require('zone.js/dist/long-stack-trace-zone');
}

