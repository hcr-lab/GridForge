# possible solution: javascript nutzen und auf Buttons legen
# def zoomIn():
#     ui.run_javascript(f'const image = ref(img);let scale = 1;scale += 0.1;image.style.transform = scale(${scale});')

# picture now shown, but zoom not possible
zoomable_image_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Zoom with JavaScript</title>
    <style>
        .container {
            position: relative;
            width: auto;
            overflow: hidden;
        }

        .container img {
            width: 100%;
            transition: transform 0.2s;
        }
    </style>
</head>
<body>
    <div class="container">
        <img id="zoomImage" src="../uploaded_files/uploaded_file.pgm" alt="Zoomable Image">
    </div>
    <button onclick="zoomIn()">Zoom In</button>
    <button onclick="zoomOut()">Zoom Out</button>

    <script>
        let scale = 1;
        const image = document.querySelector('[data-ref="img"]');

        function zoomIn() {
            scale += 0.1;
            image.style.transform = `scale(${scale})`;
        }

        function zoomOut() {
            scale = Math.max(1, scale - 0.1);
            image.style.transform = `scale(${scale})`;
        }
    </script>
</body>
</html>
"""
# HTML, CSS, and JS for a zoomable and pannable image
# not finding the files even when served as static files. Check how to do it. but first skip it 
# TODO: enable zoom for images

# zoomable_image_html = """
# <div class="zoom-container">
#     <img id="zoomable-image" src="../uploaded_files/uploaded_file.pgm" alt="Zoomable Image">
# </div>
# <style>
# .zoom-container {
#     position: relative;
#     overflow: hidden;
#     width: 100%;
#     height: 100%;
# }
# #zoomable-image {
#     transition: transform 0.2s; /* Animation */
#     width: 100%;
#     height: auto;
# }
# </style>
# <script src="https://unpkg.com/@panzoom/panzoom/dist/panzoom.min.js"></script>
# <script>
# document.addEventListener('DOMContentLoaded', (event) => {
#     const element = document.getElementById('zoomable-image')
#     Panzoom(element, {
#         maxScale: 5,
#         minScale: 1
#     });
# });
# </script>
# """

    # ui.add_body_html(zoomable_image_html)

            # with ui.row():
            #     ui.button("zoom in", zoomIn())
            
            
            ####################################################
            #interactive_image.js, when html is added
            
#             export default {
#   template: `
#     <div :style="{ position: 'relative', aspectRatio: size ? size[0] / size[1] : undefined }">
#       <img
#         ref="img"
#         :src="computed_src"
#         :style="{ width: '100%', height: '100%', opacity: src ? 1 : 0 }"
#         @load="onImageLoaded"
#         v-on="onCrossEvents"
#         v-on="onUserEvents"
#         draggable="false"
#       />
#       <svg ref="svg" style="position:absolute;top:0;left:0;pointer-events:none" :viewBox="viewBox">
#         <g v-if="cross" :style="{ display: showCross ? 'block' : 'none' }">
#           <line :x1="x" y1="0" :x2="x" y2="100%" :stroke="cross === true ? 'black' : cross" />
#           <line x1="0" :y1="y" x2="100%" :y2="y" :stroke="cross === true ? 'black' : cross" />
#         </g>
#         <g v-html="content"></g>
#       </svg>
#       <slot></slot>
#     </div>
#   `,
#   data() {
#     return {
#       viewBox: "0 0 0 0",
#       loaded_image_width: 0,
#       loaded_image_height: 0,
#       x: 100,
#       y: 100,
#       showCross: false,
#       computed_src: undefined,
#       waiting_source: undefined,
#       loading: false,
#     };
#   },
#   mounted() {
#     setTimeout(() => this.compute_src(), 0); // NOTE: wait for window.path_prefix to be set in app.mounted()
#     const handle_completion = () => {
#       if (this.waiting_source) {
#         this.computed_src = this.waiting_source;
#         this.waiting_source = undefined;
#       } else {
#         this.loading = false;
#       }
#     };
#     this.$refs.img.addEventListener("load", handle_completion);
#     this.$refs.img.addEventListener("error", handle_completion);
#     for (const event of [
#       "pointermove",
#       "pointerdown",
#       "pointerup",
#       "pointerover",
#       "pointerout",
#       "pointerenter",
#       "pointerleave",
#       "pointercancel",
#     ]) {
#       this.$refs.svg.addEventListener(event, (e) => this.onPointerEvent(event, e));
#     }
#   },
#   updated() {
#     this.compute_src();
#   },
#   methods: {
#     compute_src() {
#       const suffix = this.t ? (this.src.includes("?") ? "&" : "?") + "_nicegui_t=" + this.t : "";
#       const new_src = (this.src.startsWith("/") ? window.path_prefix : "") + this.src + suffix;
#       if (new_src == this.computed_src) {
#         return;
#       }
#       if (this.loading) {
#         this.waiting_source = new_src;
#       } else {
#         this.computed_src = new_src;
#         this.loading = true;
#       }
#       if (!this.src && this.size) {
#         this.viewBox = `0 0 ${this.size[0]} ${this.size[1]}`;
#       }
#     },
#     updateCrossHair(e) {
#       const width = this.src ? this.loaded_image_width : this.size ? this.size[0] : 1;
#       const height = this.src ? this.loaded_image_height : this.size ? this.size[1] : 1;
#       this.x = (e.offsetX * width) / e.target.clientWidth;
#       this.y = (e.offsetY * height) / e.target.clientHeight;
#     },
#     onImageLoaded(e) {
#       this.loaded_image_width = e.target.naturalWidth;
#       this.loaded_image_height = e.target.naturalHeight;
#       this.viewBox = `0 0 ${this.loaded_image_width} ${this.loaded_image_height}`;
#       this.$emit("loaded", { width: this.loaded_image_width, height: this.loaded_image_height, source: e.target.src });
#     },
#     onMouseEvent(type, e) {
#       const imageWidth = this.src ? this.loaded_image_width : this.size ? this.size[0] : 1;
#       const imageHeight = this.src ? this.loaded_image_height : this.size ? this.size[1] : 1;
#       this.$emit("mouse", {
#         mouse_event_type: type,
#         image_x: (e.offsetX * imageWidth) / this.$refs.img.clientWidth,
#         image_y: (e.offsetY * imageHeight) / this.$refs.img.clientHeight,
#         button: e.button,
#         buttons: e.buttons,
#         altKey: e.altKey,
#         ctrlKey: e.ctrlKey,
#         metaKey: e.metaKey,
#         shiftKey: e.shiftKey,
#       });
#     },
#     onPointerEvent(type, e) {
#       const imageWidth = this.src ? this.loaded_image_width : this.size ? this.size[0] : 1;
#       const imageHeight = this.src ? this.loaded_image_height : this.size ? this.size[1] : 1;
#       this.$emit(`svg:${type}`, {
#         type: type,
#         element_id: e.target.id,
#         image_x: (e.offsetX * imageWidth) / this.$refs.svg.clientWidth,
#         image_y: (e.offsetY * imageHeight) / this.$refs.svg.clientHeight,
#       });
#     },
#   },
#   computed: {
#     onCrossEvents() {
#       if (!this.cross) return {};
#       return {
#         mouseenter: () => (this.showCross = true),
#         mouseleave: () => (this.showCross = false),
#         mousemove: (event) => this.updateCrossHair(event),
#       };
#     },
#     onUserEvents() {
#       const events = {};
#       for (const type of this.events) {
#         events[type] = (event) => this.onMouseEvent(type, event);
#       }
#       return events;
#     },
#   },
#   props: {
#     src: String,
#     content: String,
#     size: Object,
#     events: Array,
#     cross: Boolean,
#     t: String,
#   },
# };
