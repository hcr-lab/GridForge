export default {
    template: `
    <div class="container" style="position: relative; width: 300px; overflow: hidden;">
        <button @click="zoomIn">Zoom In</button>
        <button @click="zoomOut">Zoom Out</button>
    </div>`,
    data() {
        return {
          scale: 1,
          img: null,
        };
      },
      mounted() {
        // Select the external image element after the component has been mounted
        this.img = document.querySelector('[data-ref="img"]');
        if (this.img) {
            console.log('Image element found:', this.img);
            this.img.style.transition = 'transform 0.2s'; // Add smooth transition
          } else {
            console.log('Image element not found');
          }
      },
      methods: {
        zoomIn() {
          this.scale += 0.1;
          this.updateImageScale();
        },
        zoomOut() {
          this.scale = Math.max(1, this.scale - 0.1);
          this.updateImageScale();
        },
        // cannot find the correct properties to transform
        updateImageScale() {
            if (this.img) {
                console.log(`Scaling image to: ${this.scale}`);
                this.img.style.transform = `scale(${this.scale})`;
              }
              else {
                console.log(`no image found, scale is ${this.scale}`);
              }
        }
      },
      props: {},
      style: {
        // img: {
        //     innerWidth: 100%,
        //     trans
        // }
      }
    };


