import { RepositoryService } from './repository.service';
import { Repository } from './repository.model';
import { ManageSettingsComponent } from './management/manage-settings.component';

describe('Attachment cleanup', () => {
    const repository = {urls: {purge_attachments: '/purge/'}} as Repository;

    it('continues batches with the same cutoff and finishes only on 204', (done: any) => {
        const replies = [
            {status: 202, json: () => ({through_id: 12})},
            {status: 202, json: () => ({through_id: 12})},
            {status: 204}
        ];
        const post = jasmine.createSpy('post').and.callFake(() => ({
            toPromise: () => Promise.resolve(replies.shift())
        }));
        const service = new RepositoryService({post} as any);
        service.purgeAttachmentData(repository).then(() => {
            expect(post.calls.allArgs()).toEqual([
                ['/purge/', {through_id: null}],
                ['/purge/', {through_id: 12}],
                ['/purge/', {through_id: 12}]
            ]);
            done();
        }).catch(done.fail);
    });

    it('stops on failure without an automatic retry or a success message', (done: any) => {
        let failRequest: (reason: any) => void;
        const post = jasmine.createSpy('post').and.returnValue({
            toPromise: () => new Promise((resolve, reject) => { failRequest = reject; })
        });
        const service = new RepositoryService({post} as any);
        const component = new ManageSettingsComponent(null, service);
        component.repository = repository;
        component.purge();
        component.purge();
        expect(component.purging).toBe(true);
        expect(component.dataDeleted).toBe(false);
        expect(post.calls.count()).toBe(1);
        failRequest(new Error('storage unavailable'));
        setTimeout(() => {
            expect(component.purging).toBe(false);
            expect(component.purgeFailed).toBe(true);
            expect(component.dataDeleted).toBe(false);
            expect(post.calls.count()).toBe(1);
            post.and.returnValue({toPromise: () => Promise.resolve({status: 204})});
            component.purge();
            setTimeout(() => {
                expect(component.purging).toBe(false);
                expect(component.purgeFailed).toBe(false);
                expect(component.dataDeleted).toBe(true);
                done();
            }, 0);
        }, 0);
    });

    it('does not restart cleanup if the server omits its cutoff', (done: any) => {
        const post = jasmine.createSpy('post').and.returnValue({
            toPromise: () => Promise.resolve({status: 202, json: (): any => ({})})
        });
        new RepositoryService({post} as any).purgeAttachmentData(repository)
            .then(() => done.fail('Expected cleanup to stop'))
            .catch(() => {
                expect(post.calls.count()).toBe(1);
                done();
            });
    });
});
