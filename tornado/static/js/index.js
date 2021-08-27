const openPostModal = postId => {
  document.getElementById(`post-modal-${postId}`)
    ?.classList.add("open-modal");
  console.log(postId);
};

const closePostModal = postId => {
  document.getElementById(`post-modal-${postId}`)
    ?.classList.remove("open-modal");
  console.log(postId);
};
