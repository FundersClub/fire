import { Repository } from '../repository/repository.model';

export class AssociateEmail {
    constructor(
        public email: string, // Email to associate
        public repository: Repository,
        public url: string,
        public login?: string // Github username, null if no association
    ) {}
}
