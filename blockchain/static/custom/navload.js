$.ajax({
    url: '/nav',
    type: 'GET',
    data: {
        select: `${$('meta[name=select]').attr("content")}`
    },
    success: (response) => {
        $('body').append(response)
    }
});