import { Injectable, Inject } from '@angular/core';
import { DOCUMENT } from '@angular/platform-browser'

@Injectable()
export class OauthUrlService {
    readonly oAuthUrlBase = '/accounts/github/login/?process=login&next=';

    constructor(
        @Inject(DOCUMENT) private document: any
    ) {}

    get(returnTo: string): string {
        return this.document.location.origin + this.oAuthUrlBase + returnTo;
    }
}
