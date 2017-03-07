import { Inject, Injectable } from '@angular/core';
import { Http } from '@angular/http';

import 'rxjs/add/operator/toPromise';

import { INITIAL_DATA_CACHE } from '../initial-data-cache';
import { RepositoryService } from '../repository/repository.service';
import { User } from './user.model';

@Injectable()
export class UserService {
    private getUserDataUrl = '/api/github/me/';
    userData: Promise<User>;

    constructor(
        private http: Http,
        @Inject(INITIAL_DATA_CACHE) cachedUserData: User,
        private repositoryService: RepositoryService
    ) {
        this.userData = new Promise((resolve, reject) => {
            // Check if we've got a server-provided cache of this data.
            // Boolean check is for sanity; existence of object should be enough
            // to consider is usable.
            if (cachedUserData && typeof cachedUserData.is_authenticated == 'boolean') {
                this.processUserData(cachedUserData);
                resolve(cachedUserData);
            } else {
                this.http.get(this.getUserDataUrl).toPromise()
                    .then((response) => {
                        let user = response.json() as User;
                        this.processUserData(user);
                        resolve(user);
                    })
                    .catch((error: any) => reject(error));
                }
            }
        );
    }

    private processUserData(user: User) {
        if (user && user.repositories) {
            for (let repo of user.repositories) {
                this.repositoryService.add(repo);
            }
        }
    }

    isAuthenticated(): Promise<boolean> {
        return this.userData.then((user: User) => user.is_authenticated);
    }
}
