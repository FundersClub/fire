import { Injectable } from '@angular/core';
import { Http } from '@angular/http';

import 'rxjs/add/operator/toPromise';

import { User } from './user.model';

@Injectable()
export class UserService {
    private getUserDataUrl = 'api/github/me/';

    constructor(private http: Http) { }

    getUserData(): Promise<User> {
        return this.http.get(this.getUserDataUrl)
            .toPromise()
            .then(response => response.json() as User)
            .catch(this.handleError);
    }

    private handleError(error: any): Promise<any> {
        console.error('Error', error);
        return Promise.reject(error && (error.message || error) || {});
    }

    // getUserData() {
    //     return [
    //         'Really Smart',
    //         'Super Flexible',
    //         'Super Hot',
    //         'Super Cold',
    //         'Weather Changer'
    //     ];
    // }
}
