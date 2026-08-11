import * as React from "react";
import useEmblaCarousel from "embla-carousel-react";
import { CaretLeft, CaretRight } from "@phosphor-icons/react";
import { TEST_IDS } from "@/constants/testIds";

function usePrefersReducedMotion() {
  const [reduced, setReduced] = React.useState(false);
  React.useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setReduced(mq.matches);
    update();
    mq.addEventListener("change", update);
    return () => mq.removeEventListener("change", update);
  }, []);
  return reduced;
}

interface HeroCarouselProps {
  slides: React.ReactNode[];
  ariaLabel?: string;
}

export default function HeroCarousel({ slides, ariaLabel }: HeroCarouselProps) {
  const reduced = usePrefersReducedMotion();
  const [emblaRef, emblaApi] = useEmblaCarousel({ loop: true, align: "start" });
  const [selected, setSelected] = React.useState(0);
  const [paused, setPaused] = React.useState(false);

  const scrollTo = React.useCallback((i: number) => emblaApi?.scrollTo(i), [emblaApi]);
  const scrollPrev = React.useCallback(() => emblaApi?.scrollPrev(), [emblaApi]);
  const scrollNext = React.useCallback(() => emblaApi?.scrollNext(), [emblaApi]);

  React.useEffect(() => {
    if (!emblaApi) return;
    const onSelect = () => setSelected(emblaApi.selectedScrollSnap());
    onSelect();
    emblaApi.on("select", onSelect);
    emblaApi.on("reInit", onSelect);
    return () => {
      emblaApi.off("select", onSelect);
    };
  }, [emblaApi]);

  React.useEffect(() => {
    if (!emblaApi || reduced || paused) return;
    const id = window.setInterval(() => emblaApi.scrollNext(), 3000);
    return () => window.clearInterval(id);
  }, [emblaApi, reduced, paused]);

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowLeft") {
      e.preventDefault();
      scrollPrev();
    } else if (e.key === "ArrowRight") {
      e.preventDefault();
      scrollNext();
    }
  };

  return (
    <div
      data-testid={TEST_IDS.home.heroCarousel}
      className="relative"
      role="region"
      aria-roledescription="carousel"
      aria-label={ariaLabel}
      tabIndex={0}
      onKeyDown={onKeyDown}
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
      onFocus={() => setPaused(true)}
      onBlur={() => setPaused(false)}
    >
      <div className="overflow-hidden" ref={emblaRef}>
        <div className="flex">
          {slides.map((slide, i) => (
            <div
              key={i}
              role="group"
              aria-roledescription="slide"
              aria-label={`${i + 1} / ${slides.length}`}
              className="min-w-0 shrink-0 grow-0 basis-full"
            >
              {slide}
            </div>
          ))}
        </div>
      </div>

      {/* Arrows */}
      <button
        type="button"
        data-testid={TEST_IDS.home.heroPrev}
        onClick={scrollPrev}
        aria-label="Sebelumnya"
        className="absolute left-4 top-1/2 hidden h-11 w-11 -translate-y-1/2 items-center justify-center rounded-full border border-border bg-background/90 text-foreground shadow-sm backdrop-blur transition-colors duration-300 hover:border-gold md:flex"
      >
        <CaretLeft size={18} weight="bold" />
      </button>
      <button
        type="button"
        data-testid={TEST_IDS.home.heroNext}
        onClick={scrollNext}
        aria-label="Berikutnya"
        className="absolute right-4 top-1/2 hidden h-11 w-11 -translate-y-1/2 items-center justify-center rounded-full border border-border bg-background/90 text-foreground shadow-sm backdrop-blur transition-colors duration-300 hover:border-gold md:flex"
      >
        <CaretRight size={18} weight="bold" />
      </button>

      {/* Dots */}
      <div
        data-testid={TEST_IDS.home.heroDots}
        className="absolute bottom-6 left-1/2 flex -translate-x-1/2 items-center gap-3"
      >
        {slides.map((_, i) => (
          <button
            key={i}
            type="button"
            onClick={() => scrollTo(i)}
            aria-label={`Slide ${i + 1}`}
            aria-current={selected === i}
            className={`h-2 rounded-full transition-all duration-300 ${
              selected === i ? "w-7 bg-gold" : "w-2 bg-primary/25 hover:bg-primary/50"
            }`}
          />
        ))}
      </div>
    </div>
  );
}
