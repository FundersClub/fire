import { Injectable } from '@angular/core';
import { Http } from '@angular/http';

import 'rxjs/add/operator/toPromise';

import { AssociateEmail } from './associate-email.model';

@Injectable()
export class AssociateEmailService {
    readonly apiUrlRoot = '/api/github/associate-email/'

    constructor(
        private http: Http
    ) {}

    getByUuid(uuid: string, token?: string) {
        let url = this.apiUrlRoot + uuid + '/';
        if (token) {
            url += encodeURIComponent(token) + '/';
        }
        return new Promise((resolve, reject) => {
            this.http.get(url, {}).toPromise()
                .then((response) => resolve(response.json() as AssociateEmail))
                .catch((error) => reject(error));
            }
        );
    }

    confirmCurrentUserAssociation({url}: AssociateEmail) {
        return this.http.post(url, {}).toPromise()
    }
}
