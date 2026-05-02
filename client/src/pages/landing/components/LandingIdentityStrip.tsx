/**
 * LandingIdentityStrip
 *
 * Purpose:
 * - Horizontal scrollable strip of identity cards with images and text overlays
 * - Used multiple times throughout the landing page to showcase different identities
 * - Each card features an image background with gradient overlay and white text
 */

interface IdentityCard {
  title: string;
  imageSrc: string;
}

interface LandingIdentityStripProps {
  identities: IdentityCard[];
  alignment?: "left" | "center" | "right";
}

export default function LandingIdentityStrip({
  identities,
  alignment = "center",
}: LandingIdentityStripProps) {
  const alignmentClasses = {
    left: "justify-start",
    center: "justify-center",
    right: "justify-end",
  };

  return (
    <div className="w-full overflow-x-auto overflow-y-hidden [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
      <div
        className={`flex items-center relative shrink-0 w-full min-w-max md:min-w-0 md:w-full ${alignmentClasses[alignment]} gap-0 md:gap-0`}
      >
        {identities.map((identity, index) => (
          <div
            key={index}
            className="flex flex-col gap-2 sm:gap-[10px] items-start overflow-hidden relative shadow-[0px_1px_4px_0px_rgba(30,30,30,0.25)] shrink-0 w-[280px] sm:w-[400px] md:w-[600px] lg:w-[800px] xl:w-[1080px] h-[200px] sm:h-[300px] md:h-[400px] lg:h-[500px] xl:h-[608px]"
          >
            <img
              alt={identity.title}
              className="absolute inset-0 max-w-none object-cover pointer-events-none size-full"
              src={identity.imageSrc}
            />
            <div className="bg-gradient-to-b flex from-[67.524%] from-[rgba(11,28,74,0)] gap-2 sm:gap-[10px] h-full items-end p-4 sm:p-6 md:p-8 lg:p-10 relative shadow-[2px_2px_10px_0px_rgba(0,0,0,0.8)] shrink-0 to-[rgba(11,28,74,0.7)] w-full">
              <p className="font-bold leading-normal relative shrink-0 text-base sm:text-lg md:text-xl lg:text-2xl xl:text-[30px] text-white text-nowrap tracking-tight sm:tracking-[0.4px] md:tracking-[0.6px] whitespace-pre">
                {identity.title}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

