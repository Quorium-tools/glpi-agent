"use client";

import { useEffect, useState } from "react";

const PHRASES = [
  "pensé pour votre équipe",
  "gestion des tickets plus rapide",
  "support IT plus intelligent",
  "workflows inter-départements",
];

const TYPE_SPEED = 60;
const DELETE_SPEED = 35;
const PAUSE_AFTER_TYPE = 1600;
const PAUSE_AFTER_DELETE = 400;

export default function Typewriter() {
  const [displayed, setDisplayed] = useState("");
  const [phraseIndex, setPhraseIndex] = useState(0);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const phrase = PHRASES[phraseIndex];

    if (!deleting && displayed.length < phrase.length) {
      const t = setTimeout(
        () => setDisplayed(phrase.slice(0, displayed.length + 1)),
        TYPE_SPEED,
      );
      return () => clearTimeout(t);
    }

    if (!deleting && displayed.length === phrase.length) {
      const t = setTimeout(() => setDeleting(true), PAUSE_AFTER_TYPE);
      return () => clearTimeout(t);
    }

    if (deleting && displayed.length > 0) {
      const t = setTimeout(
        () => setDisplayed(displayed.slice(0, -1)),
        DELETE_SPEED,
      );
      return () => clearTimeout(t);
    }

    if (deleting && displayed.length === 0) {
      const t = setTimeout(() => {
        setDeleting(false);
        setPhraseIndex((i) => (i + 1) % PHRASES.length);
      }, PAUSE_AFTER_DELETE);
      return () => clearTimeout(t);
    }
  }, [displayed, deleting, phraseIndex]);

  return (
    <span className="gradient-text typewriter">
      {displayed}
      <span className="typewriter-cursor" aria-hidden />
    </span>
  );
}
