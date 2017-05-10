/* globals girderTest, describe, expect, it, runs, waits, waitsFor  */

girderTest.addCoveredScripts([
    '/clients/web/static/built/plugins/candela/plugin.min.js'
]);

girderTest.startApp();

$(function () {
    describe('Test the candela UI.', function () {

        it('register a user', girderTest.createUser(
            'johndoe', 'john.doe@email.com', 'John', 'Doe', 'password!'
        ));

        it('uploads the data file', function () {
            runs(function () {
                expect($('#g-user-action-menu.open').length).toBe(0);
                $('.g-user-text>a:first').click();
            });
            girderTest.waitForLoad();

            runs(function () {
                expect($('#g-user-action-menu.open').length).toBe(1);
                $('a.g-my-folders').click();
            });
            girderTest.waitForLoad();

            runs(function () {
                $('a.g-folder-list-link:last').click();
            });
            girderTest.waitForLoad();

            waitsFor(function () {
                return $('ol.breadcrumb>li.active').text() === 'Public' &&
                       $('.g-empty-parent-message:visible').length === 1;
            }, 'descending into Public folder');

            girderTest.binaryUpload('clients/web/test/testFile.csv');

            runs(function () {
                $('.g-item-list-link:first').click();
            });
        });

        it('sets up candela inputs and renders the visualization', function () {
            waitsFor(function () {
                return $('.g-item-candela-component').length === 1;
            }, 'the candela component selector to appear');

            runs(function () {
                expect($('.g-item-candela-component option').length).toBeGreaterThan(18);
                $('.g-item-candela-component').val('BarChart').change();
            });

            waitsFor(function () {
                var inputs = $('.g-candela-inputs-container').children().eq(1).children().children();
                return inputs.length === 6;
            }, 'the bar chart options to be available');

            runs(function () {
                var inputs = $('.g-candela-inputs-container').children().eq(1).children().children();
                expect(inputs.eq(0).find('label').text()).toBe('Width');
                expect(inputs.eq(1).find('label').text()).toBe('Height');
                expect(inputs.eq(2).find('label').text()).toBe('x');
                var values = [];
                for (var i = 0; i < 4; i += 1) {
                    values.push(inputs.eq(2).find('option').eq(i).text());
                }
                values.sort();
                expect(values).toEqual(['(none)', 'a_b', 'c', 'id']);
                expect(inputs.eq(3).find('label').text()).toBe('y');
                expect(inputs.eq(4).find('label').text()).toBe('color');
                expect(inputs.eq(5).find('label').text()).toBe('hover');
                $('.g-candela-update-vis').click();
            });

            waitsFor(function () {
                return $('.g-candela-vis').find('canvas').length === 1;
            }, 'the vis canvas to be drawn');

            runs(function () {
                $('.g-item-candela-component').val('TreeHeatmap').change();
            });

            waitsFor(function () {
                var inputs = $('.g-candela-inputs-container').children().eq(1).children().children();
                return inputs.length === 9;
            }, 'the visualization type to change');

            runs(function () {
                var inputs = $('.g-candela-inputs-container').children().eq(1).children().children();
                expect(inputs.eq(2).find('label').text()).toBe('Identifier column');
                expect(inputs.eq(3).find('label').text()).toBe('Color scale');
                expect(inputs.eq(3).find('option').eq(1).text()).toBe('row');
            });
        });
    });
});
