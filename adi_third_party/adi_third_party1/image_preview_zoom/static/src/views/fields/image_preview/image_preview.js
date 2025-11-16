odoo.define('image_preview_zoom.image_preview_fields', function (require) {
    "use strict";
    var basicFields = require('web.basic_fields');
    var FieldBinaryImage = basicFields.FieldBinaryImage;
    var registry = require('web.field_registry');


    const {useRef, useState} = owl.hooks;
    const MIN_SCALE = 0.5;
    const SCROLL_ZOOM_STEP = 0.1;
    const ZOOM_STEP = 0.5;


    class AttachmentViewer extends owl.Component {
        static template = 'image_preview_zoom.AttachmentViewer';

        constructor(imageUrl, displayName, ...args) {
            super(...args);
            this.MIN_SCALE = MIN_SCALE;
            this._isDragging = false;
            this._zoomerRef = useRef('zoomer');
            this._image = useRef('image');
            this._translate = {x: 0, y: 0, dx: 0, dy: 0};
            this._onClickGlobal = this._onClickGlobal.bind(this);
            this.state = useState({imageStyle: 'transform: scale3d(1, 1, 1) rotate(0deg);max-height: 100%; max-width: 100%;'});
            this.attachmentViewer = {scale: 1, angle: 0, imageUrl: imageUrl, displayName: displayName};
        }

        mounted() {
            this.el.focus();
            document.addEventListener('click', this._onClickGlobal);
        }

        willUnmount() {
            document.removeEventListener('click', this._onClickGlobal);
        }

        _update(obj) {
            Object.assign(this.attachmentViewer, obj)
        }

        get imageStyle() {
            const attachmentViewer = this.attachmentViewer;
            let style = `transform: scale3d(${attachmentViewer.scale}, ${attachmentViewer.scale}, 1) rotate(${attachmentViewer.angle}deg);`;
            if (attachmentViewer.angle % 180 !== 0) {
                style += `max-height: ${window.innerWidth}px; max-width: ${window.innerHeight}px;`;
            } else {
                style += `max-height: 100%; max-width: 100%;`;
            }
            this.state.imageStyle = style;
            return style;
        }

        isCloseable() {
            return !this._isDragging;
        }

        _close() {
            this.destroy();
            // this.attachmentViewer.close();
        }

        _download() {
            var base64Regex = /^data:image/;
            if (base64Regex.test(this.attachmentViewer.imageUrl)) {
                return
            }
            // this.attachmentViewer.attachment.download();
            const downloadLink = document.createElement('a');
            downloadLink.setAttribute('href', this.attachmentViewer.imageUrl);
            // Adding 'download' attribute into a link prevents open a new tab or change the current location of the window.
            // This avoids interrupting the activity in the page such as rtc call.
            downloadLink.setAttribute('download', '');
            downloadLink.click();
        }

        _print() {
            const printWindow = window.open('about:blank', '_new');
            printWindow.document.open();
            printWindow.document.write(`
            <html>
                <head>
                    <script>
                        function onloadImage() {
                            setTimeout('printImage()', 10);
                        }
                        function printImage() {
                            window.print();
                            window.close();
                        }
                    </script>
                </head>
                <body onload='onloadImage()'>
                    <img src="${this.attachmentViewer.imageUrl}" alt=""/>
                </body>
            </html>`);
            printWindow.document.close();
        }

        _rotate() {
            this._update({angle: this.attachmentViewer.angle + 90});
            this.imageStyle;
        }

        _stopDragging() {
            this._isDragging = false;
            this._translate.x += this._translate.dx;
            this._translate.y += this._translate.dy;
            this._translate.dx = 0;
            this._translate.dy = 0;
            this._updateZoomerStyle();
        }

        _updateZoomerStyle() {
            const attachmentViewer = this.attachmentViewer;
            const image = this._image.el;
            const tx = image.offsetWidth * attachmentViewer.scale > this._zoomerRef.el.offsetWidth
                ? this._translate.x + this._translate.dx
                : 0;
            const ty = image.offsetHeight * attachmentViewer.scale > this._zoomerRef.el.offsetHeight
                ? this._translate.y + this._translate.dy
                : 0;
            if (tx === 0) {
                this._translate.x = 0;
            }
            if (ty === 0) {
                this._translate.y = 0;
            }
            this._zoomerRef.el.style = `transform: translate(${tx}px, ${ty}px)`;
        }

        _zoomIn({scroll = false} = {}) {
            this._update({
                scale: this.attachmentViewer.scale + (scroll ? SCROLL_ZOOM_STEP : ZOOM_STEP),
            });
            this.imageStyle;
            this._updateZoomerStyle();
        }

        _zoomOut({scroll = false} = {}) {
            if (this.attachmentViewer.scale === MIN_SCALE) {
                return;
            }
            const unflooredAdaptedScale = (
                this.attachmentViewer.scale -
                (scroll ? SCROLL_ZOOM_STEP : ZOOM_STEP)
            );
            this._update({
                scale: Math.max(MIN_SCALE, unflooredAdaptedScale),
            });
            this.imageStyle;
            this._updateZoomerStyle();
        }

        _zoomReset() {
            this._update({scale: 1});
            this.imageStyle;
            this._updateZoomerStyle();
        }

        _onClick(ev) {
            if (this._isDragging) {
                return;
            }
            this._close();
        }

        _onClickClose(ev) {
            this._close();
        }

        _onClickDownload(ev) {
            ev.stopPropagation();
            this._download();
        }

        _onClickGlobal(ev) {
            if (!this._isDragging) {
                return;
            }
            ev.stopPropagation();
            this._stopDragging();
        }

        _onClickHeader(ev) {
            ev.stopPropagation();
        }

        _onClickImage(ev) {
            if (this._isDragging) {
                return;
            }
            ev.stopPropagation();
        }

        _onClickPrint(ev) {
            ev.stopPropagation();
            this._print();
        }

        _onClickRotate(ev) {
            ev.stopPropagation();
            this._rotate();
        }

        _onClickZoomIn(ev) {
            ev.stopPropagation();
            this._zoomIn();
        }

        _onClickZoomOut(ev) {
            ev.stopPropagation();
            this._zoomOut();
        }

        _onClickZoomReset(ev) {
            ev.stopPropagation();
            this._zoomReset();
        }

        _onKeydown(ev) {
            switch (ev.key) {
                // case 'ArrowRight':
                //     this._next();
                //     break;
                // case 'ArrowLeft':
                //     this._previous();
                //     break;
                case 'Escape':
                    this._close();
                    break;
                case 'q':
                    this._close();
                    break;
                case 'r':
                    this._rotate();
                    break;
                case '+':
                    this._zoomIn();
                    break;
                case '-':
                    this._zoomOut();
                    break;
                case '0':
                    this._zoomReset();
                    break;
                default:
                    return;
            }
            ev.stopPropagation();
        }

        _onLoadImage(ev) {
            ev.stopPropagation();
            // this._update({ isImageLoading: false });
        }

        _onMousedownImage(ev) {
            if (this._isDragging) {
                return;
            }
            if (ev.button !== 0) {
                return;
            }
            ev.stopPropagation();
            this._isDragging = true;
            this._dragstartX = ev.clientX;
            this._dragstartY = ev.clientY;
        }

        _onMousemoveView(ev) {
            if (!this._isDragging) {
                return;
            }
            this._translate.dx = ev.clientX - this._dragstartX;
            this._translate.dy = ev.clientY - this._dragstartY;
            this._updateZoomerStyle();
        }

        _onWheelImage(ev) {
            ev.stopPropagation();
            if (!this.el) {
                return;
            }
            if (ev.deltaY > 0) {
                this._zoomOut({scroll: true});
            } else {
                this._zoomIn({scroll: true});
            }
        }
    }


    var FieldBinaryImagePreview = FieldBinaryImage.extend({
        events: _.extend({}, FieldBinaryImage.prototype.events, {
            'click img': function (event) {
                this.trigger_up('bounce_edit');
                this.onClickImage(event);
            }
        }),

        onClickImage(event) {
            if (!this.value) {
                return
            }
            this.imageComponent = new AttachmentViewer(event.target.src, this.string);
            const parentNode = document.querySelector('body');
            this.imageComponent.mount(parentNode);
            if (this.viewType === "list"){
                event.stopPropagation();
            }
        }
    });

    registry.add('image_preview', FieldBinaryImagePreview)
});