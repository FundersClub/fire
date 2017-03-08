import { OpaqueToken } from '@angular/core';

// Enables us to dynmically inject serverside data to hydrate our views immediately.
// https://angular.io/docs/ts/latest/guide/dependency-injection.html
export let INITIAL_DATA_CACHE = new OpaqueToken('INITIAL_DATA_CACHE');

export function loadInitialDataCache() {
    return window['ME_DATA'];
}
