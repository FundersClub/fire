import { Repository } from './repository/repository.model';

export class User {
    constructor(
        public is_authenticated: boolean,
        public username?: string, // Github username
        public repositories?: Array<Repository>,
        public urls?: {[route: string]: string}
    ) {}
}
