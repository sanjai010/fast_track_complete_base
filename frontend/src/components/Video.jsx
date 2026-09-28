const videos = import.meta.glob("../assets/hero-car.mp4", {
  eager: true,
  query: "?url",
  import: "default",
});

const video = videos["../assets/hero-car.mp4"];

function Video() {
  if (!video) return null;

  return (
    <video
      autoPlay
      loop
      muted
      playsInline
      className="absolute inset-0 h-full w-full object-cover object-[70%_center]"
    >
      <source src={video} type="video/mp4" />
    </video>
  );
}

export default Video;
